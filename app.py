from h2o_wave import Q, main, app, ui
import socket
import asyncio
from models import call_to_llm2, h2ogpteCall
from prompts import webp,system_prompt, system_prompt_port_report, system_promptOS, yaraRulePrompt
import pandas as pd
import os
import re
import base64


def encode_image_to_base64(path: str) -> str:
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


base64_image1 = encode_image_to_base64("static/dark.png")
darkImage = f"data:image/jpeg;base64,{base64_image1}"

base64_image1 = encode_image_to_base64("static/light.png")
lightImage = f"data:image/jpeg;base64,{base64_image1}"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "Unable to retrieve IP"
    finally:
        s.close()
    return local_ip

hostname = socket.gethostname()
IPAddr = get_local_ip()

@app('/')
async def serve(q: Q):
    if not q.client.initialized:
        q.client.initialized = True
        q.client.theme_dark = False
        q.client.start_session = "Start session"
        q.client.host_info = [hostname, IPAddr]
        q.client.total_vul = 0
        q.client.target_ip = ""
        q.client.blocked_ips = []
        q.client.dos_threshold = 150
        q.client.log_path = "/var/log/apache2/access.log"
        q.client.web_target = ""
        q.client.current_section = "portscan"

    if q.args.theme:
        q.client.theme_dark = not q.client.theme_dark

    if q.client.theme_dark:
        image_data_uri = lightImage
    else:
        image_data_uri = darkImage
    
    
    q.page['meta'] = ui.meta_card(box='', theme='default' if q.client.theme_dark else 'h2o-dark')

    q.page['header'] = ui.header_card(
        box='1 1 -1 1',
        title='Automated Network Security',
        subtitle=f'Local Host: {hostname} ({IPAddr})',
        image=image_data_uri,
        items=[
            ui.button(name='portscan', label='Port Scan', primary=True),
            ui.button(name='dos', label='DOS Detection', primary=True),
            ui.button(name='web', label='Malware Scanner', primary=True),
            ui.button(name='wapiti', label='Web Scanner', primary=True),
            ui.persona(title='AI Integrated', subtitle='with h2oGPTe', size='xs',
                       image='https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/8e/08/69/8e086957-a68e-b17b-b08f-6127dd9c0596/AppIcon-0-0-1x_U007emarketing-0-8-0-85-220.png/230x0w.webp'),
            ui.persona(title='AI Integrated', subtitle='with Llama 3,3', size='xs',
                       image='https://miro.medium.com/v2/resize:fit:779/1*nhQzfPFi8ZWl8Ps7VebqKw.png'),
            ui.button(name='theme', label='☀ Mode')
        ]
    )

    if q.args.portscan:
        q.client.current_section = "portscan"
    elif q.args.dos:
        q.client.current_section = "dos"
    elif q.args.web:
        q.client.current_section = "web"
    elif q.args.wapiti:
        q.client.current_section = "wapiti"


    if q.client.current_section == "wapiti" or q.client.args == "urlsubmit":
        del q.page['contentOS']
        del q.page['content1_1']
        del q.page['contentYaraUpload']
        del q.page['contentYara']
        del q.page['scan_status']
        
        q.page['content'] = ui.markdown_card(
            box='1 2 5 -1',
            title='Web Scanner',
            content='Monitor and block suspicious IPs sending too many requests to your web server.'
        )

        q.page['content1'] = ui.form_card(
            box='1 3 5 -1',
            items=[
                ui.textbox(name="url",label="Enter Web URL"),
                ui.button(name="urlsubmit",label="Scan Web")
            ]
        )
        
        if q.args.urlsubmit:
            if q.args.url == "":
                q.page['meta'].dialog = ui.dialog(
                    title="Warning!",
                    items=[
                        ui.text("Please enter the web URL"),
                        ui.buttons([ui.button(name='close_dialog', label='OK', primary=True)])
                    ]
                )
            
            q.page['progress'] = ui.form_card(
                box='1 5 5 -1',
                items=[ui.progress(label='Scanning Web...', caption='This will take a few seconds')]
            )
            await q.page.save()
            
            wapiticmd = f"sudo wapiti -u {q.args.url}"

            process = await asyncio.create_subprocess_shell(
                wapiticmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
                    )
            stdout, stderr = await process.communicate()
            output = stdout.decode()
            
            match = re.search(r'(/home/[^ ]+\.html)', output)
            if match:
                report_path = match.group(1)
                try:
                    with open(report_path, "r") as html_file:
                        html_content = html_file.read()
                    
                    with open("web.txt", "w") as text_file:
                        text_file.write(html_content)
                    
                    report_new = call_to_llm2(webp, html_content,0.7)
                    print("Runnnnnn")
                    del q.page['progress']
                    q.page['progress'] = ui.markdown_card(
                        box='6 2 -1 -1',
                        title="Web Scanned Report",
                        content=report_new
                    )

                except FileNotFoundError:
                    return "Report file found in output but not accessible."
            else:
                return "Report path not found in Wapiti output."

            
            
            
            
                
            
        if q.args.close_dialog:
            q.page['meta'].dialog = None
                
    
    # ---- DOS SECTION ----
    elif q.client.current_section == "dos" or q.args.scan_dos or q.args.clear_cos or q.args.unblock_ip:
        del q.page['contentOS']
        del q.page['content1_1']
        del q.page['contentYaraUpload']
        del q.page['contentYara']
        # del q.page['scan_status']
        del q.page['content']
        del q.page['content1']
        q.page['content'] = ui.markdown_card(
            box='1 2 -1 -1',
            title='DOS Protection',
            content='Monitor and block suspicious IPs sending too many requests to your web server.'
        )

        q.page['content1'] = ui.form_card(
            box='6 2 -1 -1',
            items=[
                ui.text_l("DOS Monitoring Options", align=ui.TextAlign.CENTER),
                ui.text("/var/log/apache2/access.log"),
                ui.textbox(name='log_path', label='Server Access Log Path', value=q.client.log_path),
                ui.slider(name='threshold', label='Request Threshold', min=50, max=500, step=10, value=q.client.dos_threshold),
                ui.buttons([
                    ui.button(name='scan_dos', label='Scan DOS Attacks', primary=True),
                    ui.button(name='clear_cos', label='Unblock All', primary=True),
                ]),
                ui.dropdown(name='unblock_ip', label='Unblock Specific IP',
                            choices=[ui.choice(name=ip, label=ip) for ip in q.client.blocked_ips],
                            trigger=True),
            ]
        )

        if q.args.log_path:
            q.client.log_path = q.args.log_path
        if q.args.threshold:
            q.client.dos_threshold = q.args.threshold

        if q.args.scan_dos:
            blocked_ips = []
            bash_cmd = f"sudo tail -n 1000 {q.client.log_path} | grep -oP '^\\d+\\.\\d+\\.\\d+\\.\\d+'"
            process = await asyncio.create_subprocess_shell(bash_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            result_text = stdout.decode().strip()
            ip_list = result_text.split('\n')
            unique_ip_list = list(set(ip_list))

            for ip in unique_ip_list:
                if ip_list.count(ip) > q.client.dos_threshold and ip not in q.client.blocked_ips:
                    block_cmd = f"sudo iptables -A INPUT -s {ip} -j DROP"
                    await asyncio.create_subprocess_shell(block_cmd)
                    blocked_ips.append(ip)

            q.client.blocked_ips.extend(blocked_ips)

            blocked_text = '\n'.join([f"🚫 {ip} blocked for sending too many requests." for ip in blocked_ips])
            q.page['content2'] = ui.markdown_card(
                box='1 3 5 3',
                title='Blocked IPs (DOS Prevention)',
                content=blocked_text or "✅ No suspicious activity detected."
            )

        elif q.args.clear_cos:
            if q.client.blocked_ips:
                for ip in q.client.blocked_ips:
                    unblock_cmd = f"sudo iptables -D INPUT -s {ip} -j DROP"
                    await asyncio.create_subprocess_shell(unblock_cmd)
                q.client.blocked_ips = []
                q.page['content2'] = ui.markdown_card(box='1 3 5 3', title='Unblocked All', content="✅ All IPs have been unblocked.")
            else:
                q.page['content2'] = ui.markdown_card(box='1 3 5 3', title='Unblock All', content="ℹ️ No IPs to unblock.")

        elif q.args.unblock_ip:
            if q.args.unblock_ip in q.client.blocked_ips:
                unblock_cmd = f"sudo iptables -D INPUT -s {q.args.unblock_ip} -j DROP"
                await asyncio.create_subprocess_shell(unblock_cmd)
                q.client.blocked_ips.remove(q.args.unblock_ip)
                q.page['content2'] = ui.markdown_card(box='1 3 5 3', title='Unblock IP', content=f"✅ {q.args.unblock_ip} has been unblocked.")
            else:
                q.page['content2'] = ui.markdown_card(box='1 3 5 3', title='Unblock IP', content="⚠️ IP not in blocked list.")

    # ---- YARA Tool ----
    elif q.client.current_section == "web" or q.args.scan_web_server or q.args.update_yara or q.args.scan_yara:
        del q.page['content2']
        del q.page['contentOS']
        del q.page['content1']
        del q.page['content1_1']
        del q.page['content']
        del q.page['content1']
        q.page['content'] = ui.markdown_card(
            box='1 2 5 -1',
            title='Automated Malware Scanning using YARA',
            content="A YARA-based malware scanner identifies and classifies malware by matching specific patterns and characteristics against defined rules. It's a powerful tool for malware researchers and security analysts, enabling them to detect and categorize malicious software efficiently."
        )

        q.page['contentYara'] = ui.form_card(
            box="1 4 5 -1",
            items=[
                ui.file_upload(name='file_upload', label='Upload file to Scan', compact=True),
                ui.inline(items=[
                    ui.button(name="scan_yara", label="Scan", primary=True),
                    ui.toggle(name='deepscan', label='Deep Scan')
                ])
            ]
        )

        q.page['contentYaraUpload'] = ui.form_card(
            box="1 6 5 -1",
            items=[
                ui.file_upload(name='file_upload_to_yara', label='Upload file to Update Rulebase', compact=True),
                ui.inline(
                    items = [
                        ui.button(name="update_yara", label="Update Rulebase"),
                        ui.button(name="clear_custom", label="Clear Secondary Rulebase")
                    ]
                )
            ]
        )

        if q.args.clear_custom:
            custom_path = 'rules/malware/customDatabase.yar'
            large_custom_path = 'rules/large/customDatabaseLarge.yar'

            if os.path.exists(custom_path) or os.path.exists(large_custom_path):
                if os.path.exists(custom_path):
                    os.remove(custom_path)
                if os.path.exists(large_custom_path):
                    os.remove(large_custom_path)

                q.page['meta'].dialog = ui.dialog(
                    title="Done!",
                    items=[
                        ui.text("🧹 Rulebase has been successfully cleared."),
                        ui.buttons([ui.button(name='close_dialog', label='OK', primary=True)])
                    ]
                )
            else:
                q.page['meta'].dialog = ui.dialog(
                    title="Already Cleared",
                    items=[
                        ui.text("ℹ️ No custom rulebase found to clear."),
                        ui.buttons([ui.button(name='close_dialog', label='OK', primary=True)])
                    ]
                )

            
        
        if q.args.update_yara and q.args.file_upload_to_yara:
            q.page['progress'] = ui.form_card(
                box='1 6 5 -1',
                items=[ui.progress(label='Generating Rule...', caption='This will take a few seconds')]
            )
            await q.page.save()
            uploaded_file_path = q.args.file_upload_to_yara[0]  # Take first uploaded file

            # Download file to a local path
            local_path = f'temp_uploads/{os.path.basename(uploaded_file_path)}'
            os.makedirs('temp_uploads', exist_ok=True)
            await q.site.download(uploaded_file_path, local_path)

            try:
                with open(local_path, 'r') as f:
                    file_content = f.read()

                rule = h2ogpteCall(yaraRulePrompt, file_content)
                # rule = call_to_llm2(yaraRulePrompt, file_content, 0.7)
                await q.page.save()

                with open('rules/malware/customDatabase.yar', 'a') as f:
                    f.write('\n' + rule.strip() + '\n')

                with open('rules/large/customDatabaseLarge.yar', 'a') as f:
                    f.write('\n' + rule.strip() + '\n')

            except Exception as e:
                q.page['contentYaraUploadNew'] = ui.form_card(
                    box="1 8 5 -1",
                    items=[
                        ui.text_s("❌ Error reading uploaded file."),
                        ui.text(str(e)),
                    ]
                )

            del q.page['progress']
            q.page['meta'].dialog = ui.dialog(
                title="Rule Injected",
                items=[
                    ui.text("Rule injected into malware DB. System fortified."),
                    ui.buttons([ui.button(name='close_dialog', label='OK', primary=True)])
                ]
            )

            if q.args.close_dialog:
                q.page['meta'].dialog = None

        if q.args.scan_yara:
            scan_items = []

            q.page['progress'] = ui.form_card(
                box='1 4 5 -1',
                items=[ui.progress(label='Scanning with Rulebase', caption='This will take a few seconds')]
            )

            q.page['scan_status'] = ui.form_card(
                box='6 2 -1 -1',
                title='Scan Status in Malware Rules',
                items=scan_items
            )
            await q.page.save()

            # 🔽 Download the uploaded file to a local path
            uploaded_wave_path = q.args.file_upload[0]
            uploaded_filename = os.path.basename(uploaded_wave_path)
            local_uploaded_path = f'temp_uploads/{uploaded_filename}'
            os.makedirs('temp_uploads', exist_ok=True)
            await q.site.download(uploaded_wave_path, local_uploaded_path)

            if q.args.deepscan == False:
                directory_path = 'rules/malware'
            else:
                directory_path = "rules/large"

            for filename in os.listdir(directory_path):
                rule_path = os.path.join(directory_path, filename)
                if os.path.isfile(rule_path):
                    scan_items.append(ui.text(f"✅ Scanning rule: {filename}"))
                    q.page['scan_status'].items = scan_items
                    await q.page.save()

                    yara_cmd = f"yara {rule_path} {local_uploaded_path}"

                    process = await asyncio.create_subprocess_shell(
                        yara_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()

                    if stdout and len(stdout) > 5:
                        scan_items.append(ui.text(f"❌ Malware detected using rule path: {rule_path} **{stdout.decode().strip()}**"))
                        q.page['scan_status'].items = scan_items
                        await q.page.save()
                        break

                    if 'virus' in filename.lower():
                        q.page['scan_status'].items = scan_items
                        await q.page.save()
                        break
            else:
                scan_items.append(ui.text("🎉 Scan completed. No malware found."))
                q.page['scan_status'].items = scan_items
                q.page['meta'].dialog = ui.dialog(
                    title="✅ Scan Completed",
                    items=[
                        ui.text("🛡️ File scan completed. No known threats or malicious patterns were found."),
                        ui.buttons([ui.button(name='close_dialog', label='OK', primary=True)])
                    ]
                )
                await q.page.save()

            del q.page['progress']
            if stdout and len(stdout) > 5:
                q.page['meta'].dialog = ui.dialog(
                    title="✅ Scan Completed",
                    items=[
                        ui.text(f"⚠️ Malware detected — the file triggered the YARA rule: **{stdout.decode().strip()}**."),
                        ui.buttons([ui.button(name='close_dialog', label='OK', primary=True)])
                    ]
                )

            if q.args.close_dialog:
                q.page['meta'].dialog = None

    # ---- PORT SCAN SECTION ----
    else:
        q.client.current_section = "portscan"
        del q.page['content2']
        del q.page['contentYaraUpload']
        del q.page['contentYara']
        # del q.page['scan_status']
        del q.page['content']
        del q.page['content1']
        q.page['content'] = ui.markdown_card(
            box='1 2 -1 -1',
            title='Port Scan',
            content='Scan for open ports on a given IP using Nmap.'
        )

        q.page['content1'] = ui.form_card(
            box='1 3 4 3',
            items=[
                ui.text_l("Scan Port Details", align=ui.TextAlign.CENTER),
                ui.textbox(name='targetip', label="Target IP"),
                ui.button(name='nmap_start', label="Scan"),
                ui.text(f"Port found: {q.client.total_vul}"),
            ]
        )

        if q.args.nmap_start:
            if not q.args.targetip:
                q.page['meta'].dialog = ui.dialog(
                    title="Error",
                    items=[ui.text("Please enter a target IP before scanning."),
                           ui.buttons([ui.button(name='close_dialog', label='OK', primary=True)])]
                )
            else:
                q.client.target_ip = q.args.targetip
                q.page['content1_1'] = ui.form_card(
                    box='5 3 -1 2',
                    items=[ui.progress(label=f'Scanning IP: {q.client.target_ip}', caption='Please wait...')]
                )
                await q.page.save()

                nmap_command = f"sudo nmap -sV -O -Pn --host-timeout 120s {q.client.target_ip}"
                process = await asyncio.create_subprocess_shell(nmap_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await process.communicate()

                if stdout:
                    result_text = stdout.decode().strip()
                    csv_text = call_to_llm2(system_prompt, result_text, 0)
                    csvOS = call_to_llm2(system_promptOS, result_text, 0)
                    port_details_path = "OUTPUT_FILES/port_details.csv"
                    with open(port_details_path, "w") as f:
                        f.write(csv_text)

                    csv_text_report = call_to_llm2(f"Target IP is {q.client.target_ip}, {system_prompt_port_report}", csv_text, 0)
                    port_report_path = "OUTPUT_FILES/port_report.csv"
                    with open(port_report_path, "w") as f:
                        f.write(csv_text_report)

                    df = pd.read_csv(port_report_path)
                    q.client.total_vul = len(df)
                    uploaded_files = await q.site.upload([port_report_path])
                    document_path = uploaded_files[0] if uploaded_files else None

                    table_items = [ui.text_l(f"Scan Results for the IP: {q.client.target_ip}")]
                    if document_path:
                        table_items.append(ui.link(label="Download CSV", path=document_path, download=True))
                        table_rows = [ui.table_row(name=str(row[0]), cells=[str(row[col]) for col in df.columns]) for _, row in df.iterrows()]
                        table_items.append(ui.table(name='port_table', columns=[ui.table_column(name=col, label=col) for col in df.columns], rows=table_rows, downloadable=True))
                    else:
                        table_items.append(ui.text("No scan report available."))

                    q.page['content1_1'] = ui.form_card(box="5 3 -1 -1", items=table_items)

                    q.page['contentOS'] = ui.markdown_card(
                        box='1 6 4 3',
                        title='',
                        content=csvOS
                    )

        if q.args.close_dialog:
            q.page['meta'].dialog = None

    await q.page.save()

if __name__ == '__main__':
    main()
