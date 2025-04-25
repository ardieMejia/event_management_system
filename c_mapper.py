

class C_mapper:

    excelToDatabase = { "member.csv" :
                        {
                            "mcfId":"MCF_ID", 
                            "mcfName":"MCF_Name", 
                            "password":"Password", 
                            "gender":"Gender", 
                            "yearOfBirth":"Year_of_birth", 
                            "state":"State", 
                            "nationalRating":"National_Rating", 
                            "fideId":"FIDE_Id"
                           # "ID_No": "mcfId", "Name": "mcfName", "FED": "state", "birthday": "yearOfBirth", "rtg_nat": "nationalRating", "fide_no": "fideId", "rating_int": "fideRating"
                        },

                        "fide.csv" :
                        {
                            "fideId":"fideId",
                            "fideName":"fideName",
                            "fideRating":"fideRating",
                            "mcfId":"mcfId"
                           # "ID_No": "mcfId", "Name": "mcfName", "FED": "state", "birthday": "yearOfBirth", "rtg_nat": "nationalRating", "fide_no": "fideId", "rating_int": "fideRating"
                        },

                        
                        # ========== sample MCF

                        "mcf.csv":
                        {
                            "mcfId":"ID_No", 
                            "mcfName":"Name", 
                            # "password":"ID_No", 
                            "gender":"Sex", 
                            "yearOfBirth":"birthday", 
                            "state":"FED", 
                            "nationalRating":"rtg_nat", 
                            "fideId":"fide_no",
                            "events":"events"
                        },
                        # ========== sample FRL
                        "frl.csv":
                        {
                            "fideId":"ID Number",
                            "fideName":"Name",
                            "fideRating":"SRtng"
                        }
                       }
    def __init__():
        pass
        
