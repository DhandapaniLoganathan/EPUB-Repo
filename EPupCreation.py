import pymysql
import sys
import os
import zipfile
from bs4 import BeautifulSoup

#program_name = sys.argv[0]
#arguments = sys.argv[1]

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            fp =os.path.join(root, file)
            if (not fp.endswith('.csv')):
                ziph.write(os.path.join(root, file))

# Connect to the database.
try:
    connection = pymysql.connect(host='192.168.2.212',
                             user='pythondev',
                             password='@jouve123',
                             db='imep',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    if(connection.open):
        #print("DB connected successfully.")

        with connection.cursor() as cursor:
            # SQL
            file_id = input("Enter file_id : ")
            #file_id = arguments.strip()
            sql = "select image_name,image_src_path,(select short_description from imep.image_description_details idd where idd.image_id=id.file_image_id and idd.version_id=(select max(version_id) from imep.image_description_details idd1 where idd1.image_id=idd.image_id))from imep.file_image_details id where id.uploaded_file_id="+file_id+" and id.is_approved='y'"
            #sql = "select image_name,image_src_path,(select short_description from imep.image_description_details idd where idd.image_id=id.file_image_id and idd.version_id=(select max(version_id) from imep.image_description_details idd1 where idd1.image_id=idd.image_id))from imep.file_image_details id where id.uploaded_file_id="+file_id+" and id.is_approved='y' limit 1"
            cursor.execute(sql)
            #print("cursor.description: ", cursor.description)
            #alt_txt_key = list(row.keys())[-1]

            for row in cursor:
                img_id=row['image_name'].strip()
                img_src_path=row['image_src_path'].strip()
                img_alt_txt=row[list(row.keys())[-1]].strip()
                #print('\n')
                print(img_id,img_src_path,img_alt_txt)
                img_src_path=img_src_path

                soup = BeautifulSoup(open(img_src_path), "html.parser")
                for img in soup.find_all('img'):
                    if(img_id in str(img['src'])):
                        img['alt']=img_alt_txt

                html = soup.prettify(soup.original_encoding)
                with open(img_src_path, "w") as file:
                    file.write(html)

            #Output_packages/9780241341261/EPUB/xhtml/illustrations.xhtml
            split_path = img_src_path.split('/')
            output_path = split_path[0] + "/" + split_path[1]+ "/" + split_path[2]

            file_output_path=split_path[1]+'.zip'
            zipf = zipfile.ZipFile(file_output_path, 'w', zipfile.ZIP_DEFLATED)
            zipdir(output_path, zipf)
            zipf.close()

            newname = file_output_path.split('.')
            newname[-1] = 'epub'
            #print("output file : ")
            newname='.'.join(newname)

            outfolder=split_path[0]+"/"+split_path[1]+"/"+ split_path[1]+'_Output/'
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)
            newname=split_path[0]+"/"+split_path[1]+"/"+ split_path[1]+'_Output/'+newname
            #print(file_output_path+" ==> "+newname)

            output = os.rename(file_output_path, newname)
            print("Output :"+newname )
            """if os.path.exists(newname):
                print("fdfd")
                update_sql = "UPDATE `imep`.`uploaded_file_details` SET `output_epub`='"+newname+"' WHERE `uploaded_file_id`='"+file_id+"'"
                if(cursor.execute(update_sql)):
                    print("Updated in database")
            """
        connection.close()
    else:
        print("Cannot Contect With Database.")



except:
    print("Unexpected error ( Contact developer ):", sys.exc_info()[0])
    print(sys.exc_info())
    raise

finally:
    # Close connection.
    print("Program END.")