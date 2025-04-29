system_prompt = "Extract PORT,STATE,SERVICE,VERSION of each port from below nmap_output. The output should be return in CSV format. If does not found any port details output should be only column names as CSV format. Do not return anything else expect the information what I mentioned. "

user_message = """Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-03-16 15:43 +0530 Nmap scan report for 192.168.43.56 Host is up (0.00043s latency). Not shown: 977 closed tcp ports (reset) PORT STATE SERVICE VERSION 21/tcp open ftp vsftpd 2.3.4 22/tcp open ssh OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0) 23/tcp open telnet Linux telnetd 25/tcp open smtp Postfix smtpd 53/tcp open domain ISC BIND 9.4.2 80/tcp open http Apache httpd 2.2.8 ((Ubuntu) DAV/2) 111/tcp open rpcbind 2 (RPC #100000) 139/tcp open netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP) 445/tcp open netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP) 512/tcp open exec? 513/tcp open login 514/tcp open shell? 1099/tcp open java-rmi GNU Classpath grmiregistry 1524/tcp open bindshell Metasploitable root shell 2049/tcp open nfs 2-4 (RPC #100003) 2121/tcp open ftp ProFTPD 1.3.1 3306/tcp open mysql MySQL 5.0.51a-3ubuntu5 5432/tcp open postgresql PostgreSQL DB 8.3.0 - 8.3.7 5900/tcp open vnc VNC (protocol 3.3) 6000/tcp open X11 (access denied) 6667/tcp open irc UnrealIRCd 8009/tcp open ajp13 Apache Jserv (Protocol v1.3) 8180/tcp open http Apache Tomcat/Coyote JSP engine 1.1 1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service : SF-Port514-TCP:V=7.94SVN%I=7%D=3/16%Time=67D6A468%P=x86_64-pc-linux-gnu%r( SF:NULL,2C,“\x01Couldn’t\x20get\x20address\x20for\x20your\x20host\x20(Nip SF:un)\n”); MAC Address: 08:00:27:ED:E4:4C (Oracle VirtualBox virtual NIC) Device type: general purpose Running: Linux 2.6.X OS CPE: cpe:/o:linux:linux_kernel:2.6 OS details: Linux 2.6.9 - 2.6.33 Network Distance: 1 hop Service Info: Hosts: metasploitable.localdomain, irc.Metasploitable.LAN; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ . Nmap done: 1 IP address (1 host up) scanned in 63.40 seconds"""


user_message0 = """Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-03-16 15:50 +0530 Nmap done: 1 IP address (0 hosts up) scanned in 1.62 seconds"""



system_prompt_port_report = """Generate a CSV file with the following columns:
1. PORT
2. SERVICE
3. EXPLOIT SCRIPTS / TOOLS
4. EXPLOIT CODE (Full Metasploit or relevant script)
5. SECURITY RECOMMENDATIONS with Linux commands to avoid them

The CSV should contain details of each open port found in an Nmap scan, including:
- Exploitable services with known Metasploit modules or other attack scripts.
- Full exploitation scripts in multi-line format.
- Security recommendations to prevent vulnerabilities.
- If no exploit exists, mention "Base on our database, No need any protection."

The output should be formatted strictly as CSV, without additional text or formatting. If there are no possible exploit scripts and no need any recommendation, No need to fill up those.If the text does not contain any port details, Do not write anything except columns in csv format.append()
"""



system_promptOS = """
From the following nmap_output:

1. Extract the **detected Operating System** and its **version details**, such as OS family (e.g., Linux, Windows), version number, accuracy if available, and any device type mentioned.

2. Present the extracted details in **Markdown** format under the heading: 
## Detected Operating System

Use bullet points to structure the following if available:
- OS Family: ...
- Version: ...
- Accuracy: ...
- Device Type: ...
- Additional Info: ...

Do not include any port, service, or unrelated network information.

Return only the Markdown content. No introductory or extra text.
"""



yaraRulePrompt = """
You are a highly intelligent security AI trained to generate YARA rules for malware classification. 
Your task is to analyze the provided file content and produce a syntactically correct and functional YARA rule 
based solely on patterns found in the input. Return only the YARA rule — do not include explanations, comments, or formatting symbols such as triple backticks.

Focus on detecting meaningful byte patterns, strings, or unique identifiers present in the content.
Avoid generic or overly broad rules. Ensure the rule is well-structured with a `rule` name, `strings` section, and a valid `condition`.

File Content:
"""



webp = """
You are an intelligent assistant that converts Wapiti-generated HTML vulnerability reports into clear, readable Markdown text.

Extract only the meaningful information about vulnerabilities from the HTML content and summarize it in clean Markdown bullet points or short sections.

Ignore formatting, tables, and irrelevant metadata. Do not include any raw HTML or extra commentary — only output the final Markdown report.
"""