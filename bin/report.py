#!/usr/bin/env python3

import os
import re
import sys
import csv
import yaml

register_name = 'government-organisation'
register_path = './data/%s/%s.tsv' % (register_name, register_name)

repo = 'https://github.com/openregister/government-organisation-data'
repo_data = repo + '/blob/master/'

sep = '\t'


#
#  load data
#  TBD: refactor these blocks ..
#
lists = yaml.load(open('lists/index.yml'))

for l in lists:
    path = lists[l].get('path', "lists/%s/list.tsv" % (l))
    reader = csv.DictReader(open(path), delimiter=sep)
    lists[l]['fields'] = reader.fieldnames
    key = lists[l]['key'] = reader.fieldnames[0]
    lists[l]['list'] = {}
    for row in reader:
        lists[l]['list'][row[key]] = row

maps = yaml.load(open('maps/index.yml'))

for m in maps:
    path = maps[m].get('path', "maps/%s.tsv" % (m))
    if (os.path.exists(path)):
        reader = csv.DictReader(open(path), delimiter=sep)
        maps[m]['fields'] = reader.fieldnames
        maps[m]['map'] = {}
        for row in reader:
            maps[m]['map'][row[m]] = row

fixups = yaml.load(open('fixup/index.yml'))

for f in fixups:
    path = fixups[f].get('path', "fixup/%s.tsv" % (f))
    if (os.path.exists(path)):
        reader = csv.DictReader(open(path), delimiter=sep)
        key = lists[l]['key'] = reader.fieldnames[0]
        fixups[f]['fixup'] = {}
        for row in reader:
            fixups[f]['fixup'][row[key]] = row

register = {}
for row in csv.DictReader(open(register_path), delimiter=sep):
    row['map:names'] = {}
    register[row[register_name]] = row



#
#  add alternate names to the register ..
#
for n in maps['name']['map']:
    row = maps['name']['map'][n]
    if 'government-organisation' in row and row['government-organisation']:
        name = register[row['government-organisation']]['name']
        if row['name'] != name:
            register[row['government-organisation']]['map:names'][row['name'].strip()] = 1

#
#  find list items in maps
#
for l in lists:
    key = lists[l]['key']

    if key == 'government-organisation':
        m = register
    elif key in maps and 'map' in maps[key]:
        m = maps[key]['map']
        lists[l]['mapped'] = []
    else:
        m = {}

    lists[l]['mapped'] = [v for v in lists[l]['list'] if v in m and 'government-organisation' in m[v] and m[v]['government-organisation']]


#
#  Report ..
#
def header(file=sys.stdout):
    file.write("""<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.28.5/css/theme.blue.min.css" type="text/css">
<style>
body {
    font-family: "Helvetica", "Helvetica Neue";
}
h1 {
    font-size: 2em;
}
table {
    width: 100%;
}
th, td {
    text-align: left;
}
.count {
    text-align: right;
}
td {
    vertical-align: top;
}
.name {
    width: 20%;
}
td .name {
    font-weight: bold;
}

</style>
</head>
<body>
<div class="wrapper">
""")

def footer(file=sys.stdout):
    file.write("""
</div>
</body>
<script type="text/javascript" src="https://code.jquery.com/jquery-2.2.0.min.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/tablesorter/2.17.4/js/jquery.tablesorter.min.js"></script>
<script>
$(function() {
    $("#maps").tablesorter({theme : 'blue'});
    $("#lists").tablesorter({theme : 'blue'});
    $("#fixups").tablesorter({theme : 'blue'});
    $("#register").tablesorter({theme : 'blue'});
    $("#list").tablesorter({theme : 'blue'});

    $('input').each(function(){
        $(this).click(function () {
            $("._" + this.name).toggle();
            $('#names td.names').each(function () {
                $(this).parent().show();
                var count = $(this).children(':visible').length;
                if (count == 0) {
                    $(this).parent().hide();
                }
                $(this).next('td').text(count);
            });
        });
    });
});
</script>
</html>
""")

header()
print('<h1><a href="https://github.com/openregister/government-organisation-data">government-organisation-data</a> data</h1>')

#
#  Lists ..
#
print("""
<h2>Source lists</h2>
<table id="lists" class="tablesorter">
<thead>
    <tr>
      <th class='name'>List</th>
      <th>Name</th>
      <th>Map</th>
      <th>Mapped</th>
      <th class='count'>List count</th>
    </tr>
</thead>
<tbody>
""")

for key in sorted(lists):
    row = lists[key]
    print("<tr>")
    print('<td class="name"><a href="lists/%s">%s</a></td>' % (key, key))
    print("<td><a href='%s'>%s</a></td>" % (row['website'], row['name']))
    print("<td>%s</td>" % row['key'])
    print("<td>%s</td>" % (len(row['mapped'])))
    print("<td class='count'>%s</td>" % (len(row['list'])))
    print("</tr>")

print("""
</tbody>
</table>
""")

#
#  Fixups ..
#
print("""
<h2>Manual fixes</h2>
<table id="fixups" class="tablesorter">
<thead>
    <tr>
      <th class='name'>Fixup</th>
      <th>Name</th>
      <th class='count'>Count</th>
    </tr>
</thead>
<tbody>
""")

for key in sorted(fixups):
    row = fixups[key]
    if ('fixup' in row):
        path = "fixup/%s.tsv" % (key)
        print("<tr>")
        print("<td class='key'><a href='%s/%s'>%s</a></td>" % (repo, path, key))
        print("<td>%s</td>" % (row['name']))
        print("<td class='count'>%s</td>" % (len(row['fixup'])))
        print("</tr>")

print("""
</tbody>
</table>
""")

#
#  Maps ..
#
print("""
<h2>Generated maps</h2>
<table id="maps" class="tablesorter">
<thead>
    <tr>
      <th class='name'>Map</th>
      <th>Name</th>
      <th class='count'>Count</th>
    </tr>
</thead>
<tbody>
""")

for key in sorted(maps):
    row = maps[key]
    if ('map' in row):
        path = "maps/%s.tsv" % (key)
        print("<tr>")
        print("<td class='key'><a href='%s/%s'>%s</a></td>" % (repo, path, key))
        print("<td>%s</td>" % (row['name']))
        print("<td class='count'>%s</td>" % (len(row['map'])))
        print("</tr>")

print("""
</tbody>
</table>
""")

#
#  Register ..
#
print("""
<h2>Register data</h2>
<table id="register" class="tablesorter">
<thead>
    <tr>
      <th>government-organisation</th>
      <th class='name'>name</th>
      <th>website</th>
      <th>start-date</th>
      <th>end-date</th>
    </tr>
</thead>
<tbody>
""")

for key in sorted(register):
    row = register[key]
    names = " ".join(["<li>" + n for n in sorted(row['map:names'], key=lambda s: s.lower())])
    print("<tr>")
    print("<td>%s</td>" % (row['government-organisation']))
    print("<td><span class='name'>%s</span> <ul class='names'>%s</ul></td>" % (row['name'], names))
    print("<td><a href='%s'>%s</a></td>" % (row['website'], row['website']))
    print("<td>%s</td>" % (row['start-date']))
    print("<td>%s</td>" % (row['end-date']))
    print("</tr>")

print("""
</tbody>
</table>
""")

footer()

#
#  a report for each list
#
for list_name in lists:
    path = "report/lists/" + list_name
    if not os.path.exists(path):
        os.makedirs(path)

    with open(path + '/index.html', "w") as file:
        header(file=file)
        file.write('<h1><a href="../..">%s</a> data</h1>' % (register_name))
        file.write('<h2>Matched <a href="%slists/%s">%s</a> list</h1>' % (repo_data, list_name, list_name))

        file.write("""
<table id="list" class="tablesorter">
<thead>
    <tr>
""")
        file.write("<th>%s</th>" % register_name)
        for field in lists[list_name]['fields']:
            file.write("<th>%s</th>\n" % field)
        file.write("""
    </tr>
</thead>
<tbody>
""")
        for key in lists[list_name]['list']:
            row = lists[list_name]['list'][key]
            map_key = lists[list_name]['key']
            if  map_key in maps and 'map' in maps[map_key]:
                code = maps[map_key]['map'].get(key, {}).get(register_name, '')
            else:
                code = ''

            file.write("<tr>")
            file.write("<td>%s</td>" % code)
            for field in lists[list_name]['fields']:
                file.write("<td>%s</td>\n" % row[field])
            file.write("</tr>")

        file.write("""
</tbody>
</table>
""")

        footer(file=file)