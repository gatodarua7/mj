import csv
import json

file = 'municipios.csv'
json_file = 'municipios.json'

#Read CSV File
def read_csv(file, json_file):
    csv_rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        field = reader.fieldnames
        for row in reader:
            csv_rows.extend([{field[i]:row[field[i]] for i in range(len(field))}])
        convert_write_json(csv_rows, json_file)

#Convert csv data into json
# Validar quais campos serão necessarios para dar como saída.
def convert_write_json(data, json_file):
    fixtures = []
    pk = 0
    with open(json_file, "w", encoding='utf8'):
        for state_object in data:
            pk = pk + 1
            estado = state_object['codigo_uf']
            
            fixture_object = {
                "model": "localizacao.Cidade",
                "pk":pk,
                "fields":{	
                    "nome": state_object['nome'],
                    "estado": int(estado)
                }
            }

            fixtures.append(fixture_object)
        fixture_data = json.dumps(
                    fixtures, 
                    ensure_ascii=False,
                    sort_keys=False,
                    indent=4,
                    separators=(',', ': ')
        )
        fixtures_file = open(json_file, "w")
        fixtures_file.write(fixture_data)
        fixtures_file.close()


read_csv(file,json_file)