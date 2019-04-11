import pymysql.cursors
import sys
import os
from bs4 import BeautifulSoup
import shutil

program_name = sys.argv[0]
arguments = sys.argv[1]

def zipdir(path,tmpf):
    # ziph is zipfile handle
    print(str(os.getcwd())+'\\'+tmpf)
    if(os.path.exists(str(os.getcwd())+'/'+tmpf)):
        shutil.rmtree(str(os.getcwd())+'/'+tmpf)
    shutil.copytree(os.getcwd()+'/'+path, os.getcwd()+'/'+tmpf)

    for root, dirs, files in os.walk(os.getcwd()+'/'+tmpf):
        for file in files:
            fp =os.path.join(root, file)
            if (fp.endswith('.csv')):
                os.remove(fp)

    shutil.make_archive(tmpf, 'zip', os.getcwd() + '/' + tmpf)
    shutil.rmtree(str(os.getcwd()) + '/' + tmpf)

# Connect to the database.
try:
    connection = pymysql.connect(host='192.168.2.212',
                             user='pythondev',
                             password='@jouve123',
                             db='imep',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    if(connection.open):
        with connection.cursor() as cursor:
            # SQL
            #file_id = input("Enter file_id : ")
            file_id = arguments.strip()
            sql = "select image_name,image_src_path,(select short_description from imep.image_description_details idd where idd.image_id=id.file_image_id and idd.version_id=(select max(version_id) from imep.image_description_details idd1 where idd1.image_id=idd.image_id))from imep.file_image_details id where id.uploaded_file_id="+str(file_id)+" and id.is_approved='y'"
            cursor.execute(sql)

            select_sql = "select * from imep.file_chapter_details where uploaded_file_id="+str(file_id)
            img_src_path='-'
            for row in cursor:
                img_id=row['image_name'].strip()
                img_alt_txt=row[list(row.keys())[-1]].strip()

                with connection.cursor() as cursor1:
                    cursor1.execute(select_sql)
                    for row1 in cursor1:
                        print(img_id + "---->" + row1['chapter_src_path'] + "--->" + img_alt_txt)
                        img_src_path=row1['chapter_src_path']

                        soup = BeautifulSoup(open(img_src_path), "html.parser")
                        for img in soup.find_all('img'):
                            if(img_id in str(img['src'])):
                                img['alt']=img_alt_txt

                        html = soup.prettify(soup.original_encoding)
                        with open(img_src_path, "w") as file:
                            file.write(html)

            if(img_src_path!='-'):

                split_path = img_src_path.split('/')
                #output_path = split_path[0] + "/" + split_path[1]+ "/" + split_path[2]
                output_path = split_path[0] + "/" + split_path[1]

                file_output_path=split_path[1]+'.zip'
                tmpf=split_path[1]
                zipdir(output_path,tmpf)

                newname = file_output_path.split('.')
                newname[-1] = 'epub'
                newname='.'.join(newname)

                outfolder=split_path[0]+"/"+split_path[1]+"/"+ split_path[1]+'_Output/'
                if not os.path.exists(outfolder):
                    os.makedirs(outfolder)
                newname=split_path[0]+"/"+split_path[1]+"/"+ split_path[1]+'_Output/'+newname

                output = os.rename(file_output_path, newname)
                print("Output :"+newname )
                """if os.path.exists(newname):
                    update_sql = "UPDATE `imep`.`uploaded_file_details` SET `output_epub`='"+str(newname)+"', file_status = '3' WHERE `uploaded_file_id`='"+str(file_id)+"'"
                    cursor.execute(update_sql)
                    connection.commit()"""
            else:
                print("Path not found..")

        connection.close()
    else:
        print("Cannot Contect With Database.")

except:
    print("Unexpected error :", sys.exc_info()[0])
    raise

finally:
    # Close connection.
    print("Program END")
