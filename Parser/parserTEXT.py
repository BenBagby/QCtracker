from pathlib import Path
import PyPDF2

rx_dict = {
    'sample_id': re.compile(r'CERTIFICATE OF ANALYSIS\s*(?P<value>[0-9]{8}[-][0-9]{3}[A-Z])'),
    'location': re.compile(r'Well\s*:\s*(?P<value>[\S\s]*?)(?=\sSample Psig| \/ )'),
}