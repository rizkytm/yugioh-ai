import csv

input_file = 'data/yugioh_processed.csv'
rows_per_file = 1000

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # Get header row
    
    file_num = 1
    current_rows = []
    
    for i, row in enumerate(reader):
        current_rows.append(row)
        
        if len(current_rows) == rows_per_file:
            # Write to file with header
            with open(f'output_{file_num}.txt', 'w', encoding='utf-8') as out:
                writer = csv.writer(out)
                writer.writerow(header)  # Write header first
                writer.writerows(current_rows)
            
            print(f'Created output_{file_num}.txt with {len(current_rows)} rows')
            file_num += 1
            current_rows = []
    
    # Write remaining rows (if any)
    if current_rows:
        with open(f'output_{file_num}.txt', 'w', encoding='utf-8') as out:
            writer = csv.writer(out)
            writer.writerow(header)
            writer.writerows(current_rows)
        
        print(f'Created output_{file_num}.txt with {len(current_rows)} rows')