import socket
import asyncio
import os
import pandas as pd
from models import call_to_llm2
from prompts import system_prompt, system_prompt_port_report
from h2o_wave import main,app, Q, ui

master_width = 10
# Get the local IP address
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
    # Initialize client state only once
    if not q.client.initialized:
        q.client.initialized = True
        q.client.start_session = "Start session"
        q.client.host_info = [hostname, IPAddr]
        q.client.total_vul = 0
        q.client.target_ip = ""

    # UI Header
    q.page['header'] = ui.header_card(
        box='1 1 10 1',
        title='NetDefender',
        subtitle='Automated Penetration Tool',
        icon='ReportHacked',
        items=[
            ui.links(inline=True, items=[
                ui.link(label="Nmap", path="/", target="#"),
                ui.link(label="Server Protection", path="/", target="#"),
                ui.link(label="Malware Scanner", path="/", target="#"),
            ]),
        ]
    )
    q.page['footer'] = ui.footer_card(box='1 9 10 1', caption=f"&copy; 2025 NSW. All rights reserved.")

    # Introduction Card
    q.page['upper_one'] = ui.form_card(box='1 2 7 2', items=[
        ui.text(
            'NetDefender is an automated penetration tool. It identifies vulnerabilities on open ports and provides security recommendations. '
            'It also offers customizable DoS/DDoS protection and malware scanning.',
            align=ui.TextAlign.JUSTIFY),
    ])

    # Display Host Info
    q.page['session_start_info'] = ui.form_card(box='8 2 3 1', items=[
        ui.text(f"Hostname: {q.client.host_info[0]}  \n IP Address: {q.client.host_info[1]}"),
    ])

    # Display Port Scan Summary
    below_text = f"Found {q.client.total_vul} Ports" if q.client.total_vul > 0 else "No Ports Found"
    q.page['total_vulnerabilities'] = ui.form_card(
        box='8 3 3 1',
        items=[ui.text(below_text)]
    )

    # Port Scanning Section
    q.page['upper_two'] = ui.form_card(
        box="1 4 3 3",
        items=[
            ui.text_l("Scan Port Details", align=ui.TextAlign.CENTER),
            ui.textbox(name="textbox", label="Target IP"),
            ui.button(name='nmap_scan_start', label="Scan"),
        ],
    )
    # Start Nmap Scan
    if q.args.nmap_scan_start:
        q.client.target_ip = q.args.textbox
        q.client.total_vul = 0

        # Show progress bar
        q.page['upper_two_right_progress'] = ui.form_card(
            box="4 4 7 2",
            items=[ui.progress(label=f'Port Scanning for IP: {q.client.target_ip}', caption='Please wait...')]
        )
        await q.page.save()

        # Run Nmap
        nmap_command = f"sudo nmap -sV -O -Pn --host-timeout 120s {q.client.target_ip}"
        process = await asyncio.create_subprocess_shell(
            nmap_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # Remove progress indicator
        del q.page['upper_two_right_progress']

        # Process results
        result_text = stdout.decode().strip() if stdout else "No open ports found or host unreachable."
        error_text = stderr.decode().strip()

        # Convert scan result into structured CSV format using LLM
        csv_format_text = call_to_llm2(system_prompt, result_text, 0)
        port_details_path0 = "OUTPUT_FILES/port_details.csv"
        with open(port_details_path0, mode="w") as file:
            file.write(csv_format_text)

        # Generate a detailed report
        csv_format_text_for_report = call_to_llm2(
            f"Target IP is {q.client.target_ip}, {system_prompt_port_report}", csv_format_text, 0
        )
        port_report_path = "OUTPUT_FILES/port_report.csv"
        with open(port_report_path, mode="w") as file:
            file.write(csv_format_text_for_report)

        # Update vulnerability count
        df = pd.read_csv(port_report_path)
        q.client.total_vul = len(df)

        # Update vulnerability count UI
        below_text = f"Found {q.client.total_vul} Ports" if q.client.total_vul > 0 else "No Ports Found"
        del q.page['total_vulnerabilities']
        q.page['total_vulnerabilities'] = ui.form_card(
            box='8 3 3 1',
            items=[ui.text(below_text)]
        )

        # Upload CSV report
        if os.path.exists(port_report_path):
            uploaded_files = await q.site.upload([port_report_path])
            document_path = uploaded_files[0] if uploaded_files else None
        else:
            document_path = None

        # Display scan results as an interactive table
        table_items = [
            ui.text_l(f"Scan Results for the IP: {q.client.target_ip}")
        ]

        # Check if CSV file exists and show download link + table
        if document_path:
            table_items.append(ui.text("Download the full scan report:"))
            table_items.append(ui.link(label="Download CSV", path=document_path, download=True))

            # Read CSV and display as table
            table_rows = []
            for _, row in df.iterrows():
                table_rows.append(
                    ui.table_row(name=str(row[0]), cells=[str(row[col]) for col in df.columns])
                )

            table_items.append(
                ui.table(
                    name='port_table',
                    columns=[ui.table_column(name=col, label=col) for col in df.columns],
                    rows=table_rows,
                    downloadable=True
                )
            )
        else:
            table_items.append(ui.text("No scan report available."))

        # Show errors if any
        if error_text:
            table_items.append(ui.text_l("Errors:"))
            table_items.append(ui.text(error_text))

        # Update UI card with results
        q.page['upper_two_right'] = ui.form_card(box="4 4 7 5", items=table_items)

    await q.page.save()
