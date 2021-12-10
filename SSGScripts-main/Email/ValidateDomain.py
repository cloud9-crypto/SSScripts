import dns.resolver
domain = 'gmail.com'
for record in dns.resolver.resolve(domain, 'MX'):
    print(record.to_text())