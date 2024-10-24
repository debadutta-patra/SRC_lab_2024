import pandas as pd
class blast_results:
    def __init__(self):
        pass
    def load_result(self,seq_file,des_file):
        self.descriptions=pd.read_csv(des_file)
        self.descriptions['Query Cover']=self.descriptions['Query Cover'].apply(str).str.split('%',expand=True)[0]
        self.descriptions=self.descriptions.astype({'Query Cover':'float64'})
        try:
            acc_split=self.descriptions['Accession  '].str.split('"',expand=True)
            self.descriptions['Accession  ']=acc_split[3]
        except:
            pass
        seqs=[]
        with open(seq_file,"r") as seq_file:
            seq=''
            for line in seq_file:
                if line.startswith('>'):
                    if seq != '':
                        seqs.append(seq)
                    seq=''
                else:
                    seq+=line.strip()

        seqs.append(seq)
        self.descriptions['Description'].dropna(inplace=True)
        self.descriptions['Sequence']=seqs
        sname_split = self.descriptions['Scientific Name'].str.split(' ',expand=True)
        self.descriptions['Genus'] = sname_split[0]
        self.descriptions_list=self.descriptions['Description'].to_list()
        self.organism_list=self.descriptions['Scientific Name'].to_list()
        self.accession_list=self.descriptions['Accession  '].to_list()
    def merge(self,*args):
        results=[]
        for arg in args:
            results.append(arg.descriptions)
        self.descriptions = pd.concat(results)
        self.descriptions.reset_index(inplace=True, drop=True)
        self.descriptions_list=self.descriptions['Description'].to_list()
    def read_csv(self,file):
        self.__init__()
        self.descriptions=pd.read_csv(file)
        self.descriptions_list=self.descriptions['Description'].to_list()
    def add_species_from_description(self):
        des_split=self.descriptions['Description'].str.split('[',expand=True)
        self.descriptions['Species']=des_split[1].str.split(']',expand=True)[0]
    def get_length(self):
        return print(f'{len(self.descriptions)} sequences found')
    def get_species(self):
        return self.descriptions.iloc[:,1].to_list()
    def show_descriptions(self, n=0):
        if n==0:
            return self.descriptions
        elif n>0:
            return self.descriptions.head(n)
        else:
            return self.descriptions.tail(-n)
    def show_sequences(self, n=0):
        if n==0:
            return self.descriptions[['Accession  ','Sequence']]
        elif n>0:
            return self.descriptions[['Accession  ','Sequence']].head(n)
        else:
            return self.descriptions[['Accession  ','Sequence']].tail(-n)
    def remove_keywords(self, word):
        for i in range(len(self.descriptions_list)):
            try:
                if word.lower() in self.descriptions_list[i].lower():
                    self.descriptions.drop(i, inplace=True)
                    self.sequences.drop(i, inplace=True)
            except:
                pass
        return self.get_length()
    def remove_acc(self,blacklist):
        for item in blacklist:
            for i in range(len(self.accession_list)):
                try:
                    if item.lower() == self.accession_list[i].lower():
                        self.descriptions.drop(i,inplace=True)
                        self.sequences.drop(i, inplace=True)
                except:
                    pass
        return self.get_length()
    def extract_species(self,species_list):
        species_black_list=self.organism_list.copy()
        for items in species_list:
            while items in species_black_list:
                species_black_list.remove(items)
        for item in species_black_list:
            for i in range(len(self.organism_list)):
                try:
                    if item.lower() == self.organism_list[i].lower():
                        self.descriptions.drop(i,inplace=True)
                        self.sequences.drop(i, inplace=True)
                except:
                    pass
        return species_black_list
    def drop_missing(self):
        self.descriptions.dropna(inplace=True)
        return self.get_length()
    def remove_sub_species(self):
        species=self.descriptions.iloc[:,1].to_list()
        for i in range(len(species)):
            try:
                species[i]=" ".join(species[i].split()[:2])
            except:
                pass
        self.descriptions['Species']=species
        self.descriptions.drop_duplicates('Species',inplace=True)
        self.descriptions.drop(['Species'],axis=1, inplace=True)
        return self.get_length()
    def drop_dupli_accession(self):
        self.descriptions.drop_duplicates('Accession  ',inplace=True)
        return self.get_length()
    def drop_species_multi_entry(self):
        self.descriptions.drop_duplicates('Scientific Name', inplace=True)
        return self.get_length()
    def drop_multi_genus(self):
        self.descriptions.drop_duplicates('Genus',inplace=True)
        return self.get_length()
    def drop_duplicate_sequence(self):
        self.descriptions.drop_duplicates('Sequence', inplace=True)
        return self.get_length()
    def eval_cutoff(self,value):
        self.descriptions.drop(self.descriptions[self.descriptions['E value'] > value].index, inplace=True)
        return self.get_length()
    def identity_cutoff(self,value):
        self.descriptions.drop(self.descriptions[self.descriptions['Per. ident'] < value].index, inplace=True)
        return self.get_length()
    def coverage_cutoff(self,value):
        self.descriptions.drop(self.descriptions[self.descriptions['Query Cover'] < value].index, inplace=True)
        return self.get_length()
    def description_to_csv(self,out_file):
        self.descriptions.to_csv(out_file,index=False)
    def write_fasta(self,out_file):
        species = self.descriptions.iloc[:,1].to_list()
        seqs = self.descriptions['Sequence'].to_list()
        with open(out_file,'w') as file:
            for name, seq in zip(species,seqs):
                x='_'.join(name.split())
                file.write(f'>{x}\n{seq}\n')
