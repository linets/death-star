#!/usr/bin/python

from subprocess import *
import sys
import getopt
import codecs


def usage():
        print """This program will generate a tiny report with space usage per
domain and user of a Zimbra server that should be opened as a CSV file.
Usage:

-h              Print this message
-o file         The name of the file to print our report
-s server       Server name of Zimbra server
-d		Only show domains with total space usage"""


def size_suffix(bytes):
    convertion = [
        (1024 ** 5, 'P'),
        (1024 ** 4, 'T'),
        (1024 ** 3, 'G'),
        (1024 ** 2, 'M'),
        (1024 ** 1, 'K'),
        (1024 ** 0, 'B'),
        ]

    bytes = int(bytes)
    for factor, suffix in convertion:
        if bytes >= factor:
            break
    total = bytes / factor
    return str(total) + suffix


def report_get_data(server='localhost'):
    pipe = Popen('/opt/zimbra/bin/zmprov gqu ' + server,
                 shell=True, stdout=PIPE, stderr=PIPE)

    domains = {}
    while True:
        line = pipe.stdout.readline()
        if line == '':
            break
        line = str(line).replace('\n', '')

        (user, quota, used) = str(line).split(' ')

        domain = str(user).split('@')[1]

        if domain not in domains:
            domains.update({domain: {
                        'users': {},
                        'used': 0,
                        'used_str': '',
                        'quota_sum': 0
                        }})

        user_dict = {user: {
                'used': used,
                'used_str': size_suffix(used),
                'quota': quota,
                'quota_str': size_suffix(quota)
                }}

        domains[domain]['users'].update(user_dict)
        domains[domain]['used'] += int(used)
        domains[domain]['used_str'] = size_suffix(domains[domain]['used'])
        domains[domain]['quota_sum'] += int(quota)

    return domains




def report_generate(report_output, domains, domains_only=False):

    try:
        report = codecs.open(report_output, 'w')
    except:
        print "Error: What?! we can't open the damn file?"
        print sys.exc_info()[0]
        sys.exit(2)

    for domain in sorted(domains.keys()):
        if domains_only:
            report.writelines("%s , %s\n" %
                              (domain, domains[domain]['used_str']))
        else:
            report.writelines(domain + "\n")
            for user in domains[domain]['users']:
                user_data = domains[domain]['users'][user]
                report.writelines(", %s, %s, %s\n" %
                                  (user, user_data['quota_str'],
                                   user_data['used_str']))
            report.writelines(", Totals, %s, %s\n" % (
                            size_suffix(domains[domain]['quota_sum']),
                            domains[domain]['used_str']))

    report.close()


def zimbra_reports():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "o: s: hd",
                                   ["help",
                                    "output=",
                                    "server=",
                                    "domains="])
    except getopt.GetoptError:
        print "Error: please read the usage!"
        usage()
        sys.exit(2)

    server = None
    report_output = None
    domains_only = False
    for opt, arg in opts:
        if opt in ("-o", "--output"):
            report_output = arg
        elif opt in ("-s", "--server"):
            server = arg
        elif opt in ("-d", "--domains"):
            domains_only = True

    if not server or not report_output:
        print """\nThe options -s and -o are required\n"""
        usage()
        sys.exit(2)

    domains = report_get_data(server)
    report_generate(report_output, domains, domains_only)


if __name__ == "__main__":
    zimbra_reports()
