### CarInfoSpiders

 
#### 实验需求
 * 全量爬取汽车资料数据库，将其数据库数据解析之后存入db，构建汽车门户网站关键数据库。
 
### 技术选型
 * 框架   Python Spider
 * DB     MySQL 

### 实现流程
 * 1、定义数据字典，attributes.ini文件；
 * 2、执行models_spider.py脚本，爬取各级别（a、b、c、d、suv、mpv、a0、a00）所有车型数据，
      将option_url append到option_urls.log文件中，为第四步准备；
      将sale_url  append到sale_urls.log文件中，为第三步准备；
 * 3、执行sale_spider.py脚本，从sale_urls.log文件逐行获取目标url，将爬取到的sub_option_url写入sub_option_urls.log中；
 * 4、执行options_spider.py脚本，从option_urls.log文件逐行获取模板url，爬取车辆所有配置数据库，写入db。
 
### CopyRight
 * 1、本程序只用于个人学习使用，严禁在任何具有商业目的的调试或运行
 * 2、如对您有所帮助，欢迎转发并star
