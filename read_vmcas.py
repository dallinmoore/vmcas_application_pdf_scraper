import pdfplumber
import re

def extract_data(pdf_file_path):
    data_lines = []
    data_return = {'Name':[],'GRE':{},'High School':['', '', ''],'College':{}, 'GPA':[]}
    start_flag = False
    stop_flag = False
    with pdfplumber.open(pdf_file_path) as pdf:

        # grab the pertinent info
        for page in pdf.pages:
            # print(page,end='\r')
            text = page.extract_text()
            lines = text.split('\n')
            for line in lines:
                if "PPRROOFFIILLEE" in line:
                    start_flag = True
                    continue
                elif "SSUUPPPPOORRTTIINNGG IINNFFOORRMMAATTIIOONN" in line:
                    start_flag = False
                    stop_flag = True
                elif start_flag:
                    data_lines.append(line.strip())
            if stop_flag:
                break
        
    if not data_lines:
        return pdf_file_path 

    hs_flag = False
    gre_flag = False
    college_flag = False
    gpa_flag = False
    major_flag = False
    name_flag = True
    retry_flag = False
    official_gre = ""

    for line in data_lines:
        # name info
        # first name, middle name, last name, DOB
        if name_flag == True:
            
            if 'MMiiddddllee NNaammee::' in line and 'FFiirrsstt NNaammee::' in line:
                match = re.search(r'MMiiddddllee NNaammee:: (.+?) ', line)
                data_return['Name'].append(match.group(1).capitalize())
            elif 'FFiirrsstt NNaammee::' in line: #'LLeeggaall FFiirrsstt NNaammee::' for 2027
                match = re.search(r'FFiirrsstt NNaammee:: ([A-Za-z\-]+)', line)
                data_return['Name'].append(match.group(1).capitalize()) #[-3] for 2027
            elif 'LLaasstt NNaammee::' in line:
                match = re.search(r'LLaasstt NNaammee:: (.+?) ', line)
                data_return['Name'].append(match.group(1).capitalize())
                name_flag = False
        elif 'DDaattee ooff BBiirrtthh::' in line:
            data_return['Name'].append(line.split()[-1])

        # high school info
        # high school, graduation date, city, state
        elif "HHIIGGHH SSCCHHOOOOLL AATTTTEENNDDEEDD" in line:
            hs_flag = True
        elif hs_flag == True:
            match = re.search(r'CCiittyy:: (.+?) D', line)
            match2 = re.search(r'CCiittyy:: (.+)', line)
            match3 = re.search(r'NNaammee:: (.+?) DDaattee', line)
            match4 = re.search(r'NNaammee:: (.+?) GGrraadd', line)
            match5 = re.search(r'SSttaattee:: (\w+)', line)
            if match:
                data_return['High School'][1] = match.group(1).title() #city
            elif match2:
                data_return['High School'][1] = match2.group(1).title() #city
            elif match3:
                data_return['High School'][0] = match3.group(1).title() #name
            elif match4:
                data_return['High School'][0] = match4.group(1).title() #name
            elif match5:
                hs_flag = False
                data_return['High School'][2] = match5.group(1) #state
            
            
        elif "SSTTAANNDDAARRDDIIZZEEDD TTEESSTTSS" == line:
            hs_flag = False
            gre_flag = True
        
        # gre info
        # Date, Verbal, Quantitative, Analytical Writing, Official/Unofficial
        
        elif gre_flag == True:
            if "OOFFFFIICCIIAALL GGRREE" == line:
                official_gre = " Official"
            elif "UUNNOOFFFFIICCIIAALL GGRREE" == line:
                official_gre = " Unofficial"
            elif line.startswith(('0', '1')):  # Check if line starts with a digit
                line = line.split()
                scores = [score for score in line if not re.search(r'\b\d+%', score)]
                if len(scores)>7 or len(scores)==5:
                    scores = scores[:1]+scores[2:]
                date = scores[0]
                del scores[0]
                scores = scores[1::2] if len(scores)>5 else scores
                scores.append(official_gre)
                data_return['GRE'][date] = scores
            elif "CCOOLLLLEEGGEESS AATTTTEENNDDEEDD" in line:
                gre_flag = False
                college_flag = True
                hs_flag = False
        elif "CCOOLLLLEEGGEESS AATTTTEENNDDEEDD" in line:
            gre_flag = False
            college_flag = True
            hs_flag = False
            
        # colleges attended info
        # college: [start date, end date, state, major, 2nd major, minor, degree, gpa]
        elif college_flag == True:
            if line[0:6].isdigit():
                words_fixed = [word[::2].title() for word in line.split()]
                college = ' '.join(words_fixed)[7:]
                data_return['College'][college]=[]
            elif "SSttaarrtt DDaattee::" in line:
                data_return['College'][college].append(line.split()[2])
            elif "EEnndd DDaattee::" in line:
                data_return['College'][college].append(line.split()[2])
            elif "SSttaattee::" in line:
                data_return['College'][college].append(line.split()[1])
            elif "MMaajjoorr" in line:
                major_flag = True
            elif major_flag == True:
                match = re.match(r'^(.*?) \/ (.*?) Degree .*?\b\w{2,3}\b (.*?) (\d{2}-\d{4})$', line)
                if match:
                    majors = match.groups()[0].split()
                    major1 = ' '.join(majors[:(round(len(majors)/2))])
                    major2 = ' '.join(majors[(round(len(majors)/2)):])
                    data_return['College'][college]+=[major1,major2]+list(match.groups())[1:]
                else:
                    data_return['College'][college]+=[line]+["","","",""]
                major_flag = False
            elif"CCOOUURRSSEEWWOORRKK" in line:
                college_flag = False

        # college gpa info
        # Undergrad Science GPA, Graduate Science GPA, Undergrad Overall GPA, Graduate Overall GPA, Overall GPA
        elif "CCAALLCCUULLAATTEEDD GGPPAA" in line: 
            gpa_flag = True
            gpa_list = ['','','','','']
        elif gpa_flag == True:
            # print(line)
            if "ggppaass bbyy sscchhooooll" in line.lower() or "ggppaa bbyy sscchhooooll" in line.lower():
                words_fixed = [word[::2].title() for word in line.split()]
                college = ' '.join(words_fixed[4:-4])
                gpa = [line.split()[-2]]
                gpa.append(line.split()[-1])
                if float(gpa[-1]) > 0:
                    try:
                        data_return['College'][college]+=gpa
                    except:
                        retry_flag = True
            elif retry_flag == True and len(line)<25:
                retry_flag == False
                college = ' '.join([college,'  '.join(line.split())[::2].title()])
                try:
                    data_return['College'][college]+=gpa
                    college = ''
                except:
                    print(college,gpa)
                    college = ''
            elif "UUnnddeerrggrraadduuaattee SScciieennccee" in line:
                gpa_list[0] = line.split()[-1]
            elif "GGrraadduuaattee SScciieennccee" in line:
                gpa_list[1] = line.split()[-1]
            elif "CCuummuullaattiivvee UUnnddeerrggrraadduuaattee Y" in line:# and len(line.split()) < 6:
                gpa_list[2] = line.split()[-1]
            elif  "GGrraadduuaattee" == line.split()[0]:
                gpa_list[3] = line.split()[-1]
            elif "OOvveerraallll" == line.split()[0] and len(line.split()) < 6:
                gpa_list[4] = line.split()[-1]
            elif "VVMMCCAASS" in line:
                data_return['GPA'] = gpa_list
                gpa_flag = False

    return data_return

# # Example usage
# pdf_file_path = 'VMCAS_PDF\\2027\\1342232063 Isabelle Hughes - Full Application PDF 2022-08-11 22 51 57 UTC.pdf'#'SHUMWAYLEAH-VMCAS.pdf' #'VMCAS_PDF\\2026\\2800059940 Kathryn A. Lewis - Full Application PDF Sep 14, 2021 at 5_12 PM (1).pdf'
# data_lines = extract_data(pdf_file_path)
# print(data_lines)
