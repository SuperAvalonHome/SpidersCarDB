#coding:UTF-8
import MySQLdb

class MysqlDB:

    def connection(self):
        try:
            self.conn = MySQLdb.connect(host='localhost',user='root',passwd='test',db='car_baseinfo',charset="utf8",port=3306)
        except MySQLdb.Error,e:
             print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        
    def query(self, sql):
        cur = self.conn.cursor()
        result = cur.execute(sql)
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()
