from prettytable import PrettyTable

def tabla(cabe,conte):
    longi=len(cabe)
    table=PrettyTable()
    table.field_names=cabe
    for row in conte:
        l=[]
        for n in range(longi):
           l.append(row[n])
        table.add_row(l)
    return(table)

