import sqlite3


class ValidScalingDB(object):
    """Create and maintain a database for validated scaling parameters."""

    def __init__(self, filename, readonly=True):
        super(ValidScalingDB, self).__init__()
        self.filename = filename
        self.readonly = readonly

        self.conn = sqlite3.connect(self.filename)
        self.cursor = self.conn.cursor()

        if not readonly:
            # Create tables
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS sounding (
                sounder text,
                datestamp text,
                fmin INTEGER,
                fmin_qd TEXT,
                foE INTEGER,
                foE_qd TEXT,
                hE real,
                hE_qd TEXT,
                foEs INTEGER,
                foEs_qd TEXT,
                fbEs INTEGER,
                fbEs_qd TEXT,
                hEs real,
                hEs_qd TEXT,
                foF1 INTEGER,
                foF1_qd TEXT,
                hF real,
                hF_qd TEXT,
                foF2 INTEGER,
                foF2_qd TEXT,
                fxI INTEGER,
                fxI_qd TEXT,
                hF2 real,
                hF2_qd TEXT,
                M3000F2 real,
                M3000F2_qd TEXT,
                huh1 real,
                huh1_qd TEXT,
                huh2 real,
                huh2_qd TEXT,
                MUF INTEGER,
                MUF_qd TEXT);''')

    def add_scaling(self, sounder, parameters):
        if self.readonly:
            raise Exception('The database was opened readonly')
        else:
            pl = []
            for k1, v1 in parameters.items():
                d = {k2: v2[0] for k2, v2 in v1.items()}
                qd = {f'{k2}_qd': v2[1] for k2, v2 in v1.items()}
                d.update(qd)
                d['datestamp'] = k1
                d['sounder'] = sounder
                pl.append(d)
                # Insert data
                # print(d)
            self.cursor.executemany('''INSERT INTO sounding VALUES (
                :sounder,
                :datestamp,
                :fmin,
                :fmin_qd,
                :foE,
                :foE_qd,
                :hE,
                :hE_qd,
                :foEs,
                :foEs_qd,
                :fbEs,
                :fbEs_qd,
                :hEs,
                :hEs_qd,
                :foF1,
                :foF1_qd,
                :hF,
                :hF_qd,
                :foF2,
                :foF2_qd,
                :fxI,
                :fxI_qd,
                :hF2,
                :hF2_qd,
                :M3000F2,
                :M3000F2_qd,
                :huh1,
                :huh1_qd,
                :huh2,
                :huh2_qd,
                :MUF,
                :MUF_qd);''', pl)

            # Save (commit) the changes
            self.conn.commit()

    def find_corrected_F2(self):
        for row in self.cursor.execute('''
                select sounder,datestamp,foF2,hF2 from sounding
                where foF2_qd='  ' and hF2_qd='  ';'''):
            print(row)

    def close_connection(self):
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        if not self.readonly:
            self.conn.commit()
        self.conn.close()

# fmin,  foE,   h'E,            foEs,  fbEs,  h'Es,  foF1,  h'F1,  foF2,  foI,   h'F2,  M3000,         MUF
# 186ES  328//  091//           000//  000EG  000//  000//  216//  043//  044//  000//  000//          000//
# 181ES  309//  096//           000//  000EG  000//  044//  202//  051//  051//  470//  262//          133//
# fmin,  foE,   h'E,   Es type, foEs,  fbEs,  h'Es,  foF1,  h'F,   foF2,  fxI,   h'F2,  M(3000)F2
# 186ES  328//  091//           000//  000EG  000//  000//  216//  048    056 X  000//  000  000  000  000//V
# 181ES  309//  096//           000//  000EG  000//  044//  202//  050    058 X  470//  262  000  000  133//V


def main():
    v = ValidScalingDB('validated_scaling.db')
    v.find_corrected_F2()


if __name__ == '__main__':
    main()
