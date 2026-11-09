import csv
import io


def _csv_text(columns, rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(columns)
    writer.writerows(rows)
    return output.getvalue()


def export_projects(projects):
    return _csv_text(("id", "name"), ((item["id"], item["name"]) for item in projects))


def export_people(people):
    raise NotImplementedError
