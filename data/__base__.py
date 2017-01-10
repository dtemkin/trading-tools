from abc import abstractmethod, ABCMeta
import csv

class Meta(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def download(self):
        raise NotImplementedError

    @abstractmethod
    def sample(self, nrows, select):
        raise NotImplementedError

    @abstractmethod
    def plot(self):
        raise NotImplementedError


class File(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def HDF5(self, driver, grp, dataset_name, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def CSV(self, delimiter, fields, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def SQL(self, dbname, tablename, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def PNG(self, img, **kwargs):
        raise NotImplementedError


class Save(File):

    def __init__(self, src):
        self.src = src
        self.config = conftools(src)
    def get_last_date(self):
        return self.config.getValue('SAVEFILE','last_date')

    def set_last_date(self, new):
        self.config.updateValue("SAVEFILE","last_date",new)

    def CSV(self, csvfile, data):
        file = getwd(csvfile+"-%s.csv" % src)


        if os.path.isfile(file):
            with open(file, mode="a", newline=nl) as f:
                writr = csv.writer(f)
                for row in data:
                    writr.writerow(list(row))
                self.set_last_date(data[:,1][len(data[:,0])-1])
                f.close()
        else:
            with open(file, mode="w", newline=nl) as file:
                writr = csv.writer(file)
                writr.writerow(["id","symbol","src","date","timestamp","opn","hi","lo","cls","vol"])
                for row in data:
                    writr.writerow(list(row))
                self.set_last_date(data[:,1][len(data[:,0])-1])
                file.close()
