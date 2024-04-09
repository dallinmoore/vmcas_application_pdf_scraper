from read_vmcas import extract_data
import os
import csv
import re


def iterate_files(folder_path):
    # List to store file paths
    file_paths = []
    
    # Iterate through every file in the folder
    for file_name in os.listdir(folder_path):
        # Get the full path of the file
        file_path = os.path.join(folder_path, file_name)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            # Append file path to the list
            file_paths.append(file_path)
        else:
            # Recursively iterate through subfolders and extend the list
            file_paths.extend(iterate_files(file_path))
    
    return file_paths


def generate_csv(data, student_id, year, student_info_file, gre_scores_file, college_info_file):
    
    # Writing Name, High School, and GPA to student_info.csv
    mode = 'w' if student_id == 1 else 'a'
    with open(student_info_file, mode, newline='') as csvfile:
        writer = csv.writer(csvfile)
        if student_id == 1:
            writer.writerow(['Student ID', 'First Name', 'Middle Name', 'Last Name', 'DOB', 'High School', 'City', 'State', 'Undergrad Science GPA', 'Graduate Science GPA', 'Undergrad Overall GPA',	'Graduate Overall GPA',	'Overall GPA', 'Class'])
        try:
            writer.writerow([student_id]+data['Name']+data['High School']+data['GPA']+[year])
        except:
            writer.writerow([student_id]+[data])
            return student_id + 1



    # Writing GRE scores to gre_scores.csv
    mode = 'w' if student_id == 1 else 'a'
    with open(gre_scores_file, mode, newline='') as csvfile:
        writer = csv.writer(csvfile)
        if student_id == 1:
            writer.writerow(['Student ID', 'Date', 'Verbal', 'Quantitative', 'Analytical Writing', 'Official?'])
        
        for date, scores in data['GRE'].items():
            writer.writerow([student_id]+scores)

    # Writing College details to college_info.csv
    mode = 'w' if student_id == 1 else 'a'
    with open(college_info_file, mode, newline='') as csvfile:
        writer = csv.writer(csvfile)
        if student_id == 1:
            writer.writerow(['Student ID', 'College', 'Start Date', 'End Date', 'State', 'Major', 'Second Major', 'Minor', 'Degree', 'Graduation Date','Graded Hours', 'GPA'])
        
        for college, details in data['College'].items():
            writer.writerow([student_id] + [college] + details)

    return student_id + 1  # Increment student ID for the next student






folder_path = 'C:/Users/04drm/OneDrive/Documents/Admission Development Comittee/VMCAS_PDF/2027'
file_paths = iterate_files(folder_path)

student_id = 1
total_files = len(file_paths)

for i, path in enumerate(file_paths):
    match = re.search(r'\\(\d{4})\\', path)
    year = match.group(1)
    data_lines = extract_data(path)
    
    generate_csv(data_lines, student_id,year, 'VMCAS_data/student_info.csv', 'VMCAS_data/gre_scores.csv', 'VMCAS_data/college_info.csv')

    student_id += 1
    
    # Calculate percentage completion
    percent_complete = (i + 1) / total_files * 100
    
    # Print percentage completion
    print(f"Progress: {percent_complete:.2f}%", end='\r')
print("Program complete.         ")