from security.vulnerability_scanner import SecurityScanner

def main():
    scanner = SecurityScanner()
    scanner.scan_system()

if __name__ == "__main__":
    main()