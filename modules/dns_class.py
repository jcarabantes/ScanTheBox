import subprocess
from modules.output import success, error, info

class Dns:

    def __init__(self, config_cls):
        self.config_cls = config_cls
        self.config = config_cls.get_yaml_content()
        self.output_file = config_cls.get_workspace() + "dns_enum.txt"

    def dns_query(self):
        output = []
        dns_server = self.config_cls.ip
        domain = self.config_cls.hostname

        record_types = ["A", "MX", "NS", "TXT", "CNAME", "SRV", "ANY"]
        for record_type in record_types:
            info(f"Dig: checking {record_type}")
            output.append(f"Dig: checking {record_type}")
            r = subprocess.run(['dig', f'@{dns_server}', domain, record_type], check=True, capture_output=True, text=True)
            print(r.stdout)
            output.append(r.stdout)

            
        # Attempt zone transfer (AXFR)
        info("Attempting zone transfer")
        output.append("Attempting zone transfer")
        r = subprocess.run(['dig', f'@{dns_server}', domain, 'AXFR'], check=True, capture_output=True, text=True)
        print(r.stdout)
        output.append(r.stdout)

        with open(self.output_file, 'a') as f:
            for result in output:
                f.write(result)
                f.write("\n")
        



