import pandas as pd
import re


class InitialsGenerator:

    def __init__(self):
        self.last_name_tag = 'Family Name'
        self.middle_initial_tag = 'Middle Initial(s)'
        self.first_name_tag = 'Surname'
        self.initials_examples = {
            "Xiang-Zhen": "X-Z",
            'Jun Soo': "J-S",
            'Baskin-Sommers': "B-S",
            'van Rooij': "vR"
        }

    def transform(self, df):

        first_name = df[self.first_name_tag]
        middle_name = df[self.middle_initial_tag]
        last_name = df[self.last_name_tag]

        for tag in [self.first_name_tag, self.middle_initial_tag, self.last_name_tag]:
            df[tag] = df[tag].apply(lambda name: name.strip() if not pd.isnull(name) else name)

        def get_first_name(first_name):
            if '-' in first_name:
                l1 = first_name.split('-')
                l = ''.join(['-'.join(l[0] for l in l1)])
            elif ' ' in first_name:
                l1 = first_name.split(' ')
                l = ''.join([' '.join(l[0] for l in l1)])
            else:
                l = first_name[0].upper()

            return l

        def get_middle(middle_initial):
            if pd.isnull(middle_initial):
                return middle_initial
            else:
                result = ''.join([x for x in middle_initial if x.isalpha()])
                if result.istitle():
                    return result[0]
                else:
                    return result


        def get_last_name(last_name):
            if '-' in last_name:
                l1 = last_name.split('-')
                l = ''.join(['-'.join(l[0] for l in l1)])
            elif ' ' in last_name:
                l1 = last_name.split(' ')
                l = ''.join([' '.join(l[0] for l in l1)])
            else:
                l = last_name[0].upper()

            return l

        fn=[]
        for i in range(len(df)):
            row = df.iloc[i, :]
            l = get_first_name(row[self.first_name_tag])
            fn.append(l)
            i=i+1

        m=[]
        for i in range(len(df)):
            row = df.iloc[i, :]
            l = get_middle(row[self.middle_initial_tag])
            m.append(l)
            i=i+1

        ln = []
        for i in range(len(df)):
            row = df.iloc[i, :]
            l = get_last_name(row[self.last_name_tag])
            ln.append(l)
            i = i + 1

        list1 = []
        for i in range(len(df)):
            dict1 = {'First name': fn[i], 'Middle Initial': m[i], self.last_name_tag: ln[i]}
            list1.append(dict1)
            i = i + 1


        def get_first_name_initial(first_name, test1, s1):
            fn_i = []
            if not len(first_name) == 1:
                for j in range(len(first_name)):
                    if '-' in first_name:

                        if j in test1:
                            l = first_name[j] + '.'
                        else:
                            l = first_name[j]
                    else:
                        l = first_name[j]
                        if ' ' in l:
                            l = s1 + l
                    fn_i.append(l)

                fn_i = [x for x in fn_i if x != ' ']
            else:
                fn_i = first_name

            return fn_i


        def get_last_name_initial(last_name, test2, s2):
            ln_i = []
            if not len(last_name) == 1:
                for j in range(len(last_name)):
                    if '-' in last_name:
                        if j in test2:
                            l = last_name[j] + '.'
                        else:
                            l = last_name[j]
                    else:
                        l = last_name[j]
                        if ' ' in l:
                            l = s2 + l
                    l = ''.join(l.split())
                    ln_i.append(l)

                ln_i = [x for x in ln_i if x != ' ']
            else:
                ln_i = last_name

            return ln_i

        #%%
        # in the widget version, we will specify this by the UI.
        # print('Eg: First Name: Xiang-Zhen')
        # g = input("Enter the initials: ")

        g = self.initials_examples['Xiang-Zhen']
        if len(g) == 0:
            print("ERROR: need initial specified for Xiang-Zhen")
            return None

        f = []
        f1 = []
        test1 = []
        for i in range(len(g)):
            if not g[i] == '.':
                f.append(i)
            else:
                f1.append(i)
        for j in range(len(f1)):
            l = f1[j] - j - 1
            test1.append(l)

        # print('Eg: First Name: Jun Soo')
        # g1 = input("Enter the initials: ")
        g1 = self.initials_examples['Jun Soo']
        if len(g1) == 0:
            print("ERROR: need initial specified for Jun Soo")
            return None

        for i in range(len(g1)):
            if not g1[i].isalpha():
                s1 = g1[i]
            else:
                s1=''

        #%%
        fn_ii=[]
        for i in range(len(df)):
            first_name=list1[i]['First name']
            l=''.join(get_first_name_initial(first_name,test1,s1))
            l1=''.join(l.split( ))
            #l=get_first_name_initial(test,list1,s)
            fn_ii.append(l1)
        fn_ii

        #%%
        # print('Eg: Last Name: Baskin-Sommers')
        # g2 = input("Enter the initials: ")
        g2 = self.initials_examples['Baskin-Sommers']
        if len(g2) == 0:
            print("ERROR: need initial specified for Baskin-Sommers")
            return None

        q = []
        q1 = []
        test2 = []
        for i in range(len(g2)):
            if not g2[i] == '.':
                q.append(i)
            else:
                q1.append(i)
        for j in range(len(q1)):
            l = q1[j] - j - 1
            test2.append(l)

        # print('Eg: Last Name: van Rooij')
        # g3 = input("Enter the initials: ")
        g3 = self.initials_examples['van Rooij']
        if len(g3) == 0:
            print("ERROR: need initial specified for van Rooij")
            return None

        for i in range(len(g3)):
            if not g3[i].isalpha():
                s2 = g3[i]
            else:
                s2=''



        #%%
        ln_ii = []
        for i in range(len(df)):
            last_name = list1[i][self.last_name_tag]
            l = ''.join(get_last_name_initial(last_name, test2, s2))
            # l1=''.join(l.split( ))
            # l=get_last_name_initial(test2,list1,s2)
            ln_ii.append(l)

        # ln_ii


        def get_initial(fn_ii,m,ln_ii):
            initial=[]
            for i in range(len(df)):
                ret = fn_ii[i]+'.'
                if not pd.isnull(m[i]):
                    for t in range(len({'Middle Initial':m[i]})):
                        ret += m[i][t]+'.'
                ret += ln_ii[i]+'.'
                initial.append(ret)
            return initial

        l=get_initial(fn_ii,m,ln_ii)

        first_name=df[self.first_name_tag]
        middle_name=df[self.middle_initial_tag]
        last_name=df[self.last_name_tag]
        data={
            "First Name": first_name,
            'Middle Initials': middle_name,
            "Last Name" :last_name,
            'first Initial':fn_ii,
            'last Initial:':ln_ii,
            'Initial':l
        }

        pd.options.display.max_rows = None
        pd.options.display.max_columns = None


        # print(pd.DataFrame(data))

        # generate_docx(l)

        return pd.DataFrame(data)


class DocGenerator:


    def __init__(self):
        self.output_doc_filename = "demo2.docx"
        self.whole_name = 'Compound Name + highest degree'
        self.affiliation_tags = [
            'Affiliation 1 Department, Institution',
            'Affiliation 2 Department, Institution',
            'Affiliation 3 Department, Institution'
        ]
        self.role_tag = 'Role(s)'
        self.roles_priority = [
            'Collected the data',
            'Conceived and designed the analysis',
            'Cohort co-investigator',
            'Contributed data or analysis tools',
            'Performed the analysis',
            'Cohort PI',
            'Read, edited and approved the paper',
            'Wrote the paper',
            'Analyzed the data'
        ]

    def get_indices_of_affiliations(self, df, affiliation_tags):

        df_affiliations = df[affiliation_tags].T
        list_of_affiliations = pd.concat([df_affiliations[name] for name in df_affiliations.columns], axis=0)

        list_of_affiliations.index = [i for i in range(len(list_of_affiliations))]
        list_of_affiliations = list_of_affiliations.to_list()

        set_of_affiliations = list(set(list_of_affiliations))
        set_of_affiliations.sort(key=list_of_affiliations.index)

        name_to_index = {name: i + 1 for (i, name) in enumerate(set_of_affiliations)}

        affiliation_indices = pd.concat([df[tag].apply(lambda x: name_to_index[x]) for tag in affiliation_tags], axis=1)

        return affiliation_indices, set_of_affiliations

    def generate(self, df, initials, old_way=False):
        # %%
        x = df[self.whole_name]

        i_inform = []

        if old_way:
            y1 = df[self.affiliation_tags[0]].tolist()
            y2 = df[self.affiliation_tags[1]].tolist()
            y3 = df[self.affiliation_tags[2]].tolist()

            for i in range(len(df)):
                i_inform.append(y1[i])
                if not pd.isnull(y2[i]):
                    i_inform.append(y2[i])
                if not pd.isnull(y3[i]):
                    i_inform.append(y3[i])

            institution = [i_inform[i] for i in range(len(i_inform))]
            ins = list(set(institution))
            ins.sort(key=institution.index)  # 运用索引
            num = []
            for i in range(len(y1)):
                for j in range(len(ins)):
                    if y1[i] == ins[j]:
                        initials = j + 1
                num.append(initials)
            num1 = []
            for i1 in range(len(y2)):
                for j1 in range(len(ins)):
                    if not pd.isnull(y2[i1]):
                        if y2[i1] == ins[j1]:
                            initials = j1 + 1
                    else:
                        initials = ''
                num1.append(initials)
            num2 = []
            for i2 in range(len(y3)):
                for j2 in range(len(ins)):
                    if not pd.isnull(y3[i2]):
                        if y3[i2] == ins[j2]:
                            initials = j2 + 1
                    else:
                        initials = ''
                num2.append(initials)
            combine = [x[i] + ' ' + str(num[i]) + ' ' + str(num1[i]) + ' ' + str(num2[i]) for i in range(len(y1))]

            # %%
            from docx import Document
            from docx.shared import Inches
            document = Document()
            document.add_heading('Authorlist', 0)
            author_text = ''
            p = document.add_paragraph('')
            for i in range(len(combine)):
                p.add_run(x[i] + ' ')
                super_text = p.add_run(str(num[i]) + ' ' + str(num1[i]) + ' ' + str(num2[i]))
                if not i == (len(combine) - 1):
                    p.add_run(',')
            document.add_paragraph('\n')
            for j in range(len(ins)):
                document.add_paragraph(ins[j], style='List Number')
            document.save('demo.docx')

        else:
            affiliation_indices, set_of_affiliations = self.get_indices_of_affiliations(df, self.affiliation_tags)
            self.generate_doc_content(df, affiliation_indices, set_of_affiliations, initials)

    def generate_doc_content(self, df, affiliation_indices, set_of_affiliations, initials):
        from docx import Document
        document = Document()
        self.generate_authorlist(affiliation_indices, df, document, set_of_affiliations)
        if self.role_tag is not None:
            self.generate_contribution_list(df, document, initials)

        document.save(self.output_doc_filename)

    def generate_authorlist(self, affiliation_indices, df, document, set_of_affiliations):
        document.add_heading('Authorlist', level=2)
        p = document.add_paragraph('')
        x = df[self.whole_name]
        for i in range(len(affiliation_indices)):
            p.add_run(x[i])
            super_text = p.add_run(", ".join([str(affiliation_indices.loc[i, tag]) for tag in self.affiliation_tags]))
            super_text.font.superscript = True
            if not i == (len(affiliation_indices) - 1):
                p.add_run(', ')
        document.add_paragraph('\n')
        for j in range(len(set_of_affiliations)):
            document.add_paragraph(set_of_affiliations[j], style='List Number')

    def generate_contribution_list(self, df, document, initials):
        flatten = lambda l: [item for sublist in l for item in sublist]

        roles = df[self.role_tag].apply(lambda x: re.split(r"\s*[;]\s*", x))
        roles_set = set(flatten(roles.to_list()))

        initials_group_by_roles = {
            tag: [] for tag in roles_set
        }

        for idx in roles.index:
            initial = initials[idx]
            for tag in roles[idx]:
                initials_group_by_roles[tag].append(initial)

        document.add_heading("Author Contributions (in alphabetical order)", level=2)

        role_set_order = self.roles_priority.copy()
        role_set_order.extend(roles_set - set(role_set_order))

        for role_name in roles_set:
            paragraph = document.add_paragraph("")
            title = paragraph.add_run(role_name)
            title.italic = True
            paragraph.add_run("\n")

            author_list = initials_group_by_roles[role_name].copy()
            author_list.sort()

            for i, author in enumerate(author_list):
                if i > 0:
                    paragraph.add_run(", ")

                paragraph.add_run(author)







    


