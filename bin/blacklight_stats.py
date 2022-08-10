import yaml
import sys

with open(sys.argv[1], 'r') as input_file:
    yaml_block = ''
    queries = 0
    failed_to_parse = 0
    search_terms = {'q': 0, 'f': 0}
    for line in input_file.readlines():
        if line.strip() == '':
            try:
                query = yaml.safe_load(yaml_block)
                if 'f' in query:
                    for term in query['f']:
                        print(f"f: {term}: {query['f'][term]}")
                        search_terms['f'] += 1
                if 'q' in query:
                    print(f"q: {query['search_field']}: {query['q']}")
                    search_terms['q'] += 1
            except:
                print('failed to parse')
                print(yaml_block)
                failed_to_parse += 1
            yaml_block = ''
            queries += 1
        yaml_block += line

print(f'queries processed: {queries}')
print(f'search terms:: {search_terms}')
print(f'failed to parse: {failed_to_parse}')

