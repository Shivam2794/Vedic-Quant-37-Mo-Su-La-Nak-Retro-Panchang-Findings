import sqlite3
import os

def build_database():
    db_path = "astrology_universe.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Building Dim_Asset_Natal...")
    cursor.execute("""
    CREATE TABLE Dim_Asset_Natal (
        Asset_ID TEXT PRIMARY KEY,
        Ticker TEXT,
        Inception_Timestamp TEXT,
        Latitude REAL,
        Longitude REAL,
        
        Sun_D1_Longitude REAL, Sun_D1_Sign TEXT, Sun_Retrograde_Flag INTEGER, Sun_Combust_Flag INTEGER,
        Moon_D1_Longitude REAL, Moon_D1_Sign TEXT, Moon_Retrograde_Flag INTEGER, Moon_Combust_Flag INTEGER,
        Mars_D1_Longitude REAL, Mars_D1_Sign TEXT, Mars_Retrograde_Flag INTEGER, Mars_Combust_Flag INTEGER,
        Mercury_D1_Longitude REAL, Mercury_D1_Sign TEXT, Mercury_Retrograde_Flag INTEGER, Mercury_Combust_Flag INTEGER,
        Jupiter_D1_Longitude REAL, Jupiter_D1_Sign TEXT, Jupiter_Retrograde_Flag INTEGER, Jupiter_Combust_Flag INTEGER,
        Venus_D1_Longitude REAL, Venus_D1_Sign TEXT, Venus_Retrograde_Flag INTEGER, Venus_Combust_Flag INTEGER,
        Saturn_D1_Longitude REAL, Saturn_D1_Sign TEXT, Saturn_Retrograde_Flag INTEGER, Saturn_Combust_Flag INTEGER,
        Rahu_D1_Longitude REAL, Rahu_D1_Sign TEXT, Rahu_Retrograde_Flag INTEGER, Rahu_Combust_Flag INTEGER,
        Ketu_D1_Longitude REAL, Ketu_D1_Sign TEXT, Ketu_Retrograde_Flag INTEGER, Ketu_Combust_Flag INTEGER,
        
        Sun_D9_Sign TEXT, Moon_D9_Sign TEXT, Mars_D9_Sign TEXT, Mercury_D9_Sign TEXT, 
        Jupiter_D9_Sign TEXT, Venus_D9_Sign TEXT, Saturn_D9_Sign TEXT, Rahu_D9_Sign TEXT, Ketu_D9_Sign TEXT,
        
        Sun_D10_Sign TEXT, Moon_D10_Sign TEXT, Mars_D10_Sign TEXT, Mercury_D10_Sign TEXT,
        Jupiter_D10_Sign TEXT, Venus_D10_Sign TEXT, Saturn_D10_Sign TEXT, Rahu_D10_Sign TEXT, Ketu_D10_Sign TEXT,
        
        Sun_Nakshatra TEXT, Sun_Pada INTEGER, Sun_KP_Sub_Lord TEXT, Sun_KP_Sub_Sub_Lord TEXT,
        Moon_Nakshatra TEXT, Moon_Pada INTEGER, Moon_KP_Sub_Lord TEXT, Moon_KP_Sub_Sub_Lord TEXT,
        
        Sun_Shadbala_Total REAL, Moon_Shadbala_Total REAL, Mars_Shadbala_Total REAL, Mercury_Shadbala_Total REAL,
        Jupiter_Shadbala_Total REAL, Venus_Shadbala_Total REAL, Saturn_Shadbala_Total REAL,
        
        SAV_Aries INTEGER, SAV_Taurus INTEGER, SAV_Gemini INTEGER, SAV_Cancer INTEGER,
        SAV_Leo INTEGER, SAV_Virgo INTEGER, SAV_Libra INTEGER, SAV_Scorpio INTEGER,
        SAV_Sagittarius INTEGER, SAV_Capricorn INTEGER, SAV_Aquarius INTEGER, SAV_Pisces INTEGER,
        
        Atmakaraka TEXT, Amatyakaraka TEXT, Darakaraka TEXT,
        Arudha_Lagna_Sign TEXT, A11_Sign TEXT, A8_Sign TEXT,
        Indu_Lagna_Longitude REAL, Bhrigu_Bindu_Longitude REAL, Hora_Lagna_Longitude REAL
    );
    """)
    
    print("Building Fact_Macro_Transit...")
    cursor.execute("""
    CREATE TABLE Fact_Macro_Transit (
        Date TEXT PRIMARY KEY,
        
        Sun_D1_Longitude REAL, Sun_Velocity REAL, Sun_Acceleration REAL, Sun_Declination REAL, Sun_OOB_Flag INTEGER, Sun_Stambhana_Flag INTEGER,
        Moon_D1_Longitude REAL, Moon_Velocity REAL, Moon_Acceleration REAL, Moon_Declination REAL, Moon_OOB_Flag INTEGER, Moon_Stambhana_Flag INTEGER,
        Mars_D1_Longitude REAL, Mars_Velocity REAL, Mars_Acceleration REAL, Mars_Declination REAL, Mars_OOB_Flag INTEGER, Mars_Stambhana_Flag INTEGER,
        Mercury_D1_Longitude REAL, Mercury_Velocity REAL, Mercury_Acceleration REAL, Mercury_Declination REAL, Mercury_OOB_Flag INTEGER, Mercury_Stambhana_Flag INTEGER,
        Jupiter_D1_Longitude REAL, Jupiter_Velocity REAL, Jupiter_Acceleration REAL, Jupiter_Declination REAL, Jupiter_OOB_Flag INTEGER, Jupiter_Stambhana_Flag INTEGER,
        Venus_D1_Longitude REAL, Venus_Velocity REAL, Venus_Acceleration REAL, Venus_Declination REAL, Venus_OOB_Flag INTEGER, Venus_Stambhana_Flag INTEGER,
        Saturn_D1_Longitude REAL, Saturn_Velocity REAL, Saturn_Acceleration REAL, Saturn_Declination REAL, Saturn_OOB_Flag INTEGER, Saturn_Stambhana_Flag INTEGER,
        
        Sun_D9_Sign TEXT, Moon_D9_Sign TEXT, Mars_D9_Sign TEXT, Mercury_D9_Sign TEXT, 
        Jupiter_D9_Sign TEXT, Venus_D9_Sign TEXT, Saturn_D9_Sign TEXT,
        
        Sun_Transit_Shadbala REAL, Moon_Transit_Shadbala REAL, Mars_Transit_Shadbala REAL,
        
        Panchang_Tithi TEXT, Panchang_Karana TEXT, Panchang_Yoga TEXT, Panchang_Vara TEXT,
        
        Eclipse_Flag INTEGER, Graha_Yuddha_Active INTEGER
    );
    """)
    
    print("Building Fact_Micro_Intraday...")
    cursor.execute("""
    CREATE TABLE Fact_Micro_Intraday (
        Timestamp TEXT PRIMARY KEY,
        RP_Day_Lord TEXT,
        RP_Moon_Sign_Lord TEXT,
        RP_Moon_Star_Lord TEXT,
        RP_Asc_Sign_Lord TEXT,
        RP_Asc_Star_Lord TEXT,
        Current_Hora_Lord TEXT,
        Choghadiya_Status TEXT,
        Active_Tattva TEXT
    );
    """)
    
    print("Building Fact_Asset_Dasha...")
    cursor.execute("""
    CREATE TABLE Fact_Asset_Dasha (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Asset_ID TEXT,
        Dasha_System TEXT,
        Start_Timestamp TEXT,
        End_Timestamp TEXT,
        Mahadasha_Lord TEXT,
        Antardasha_Lord TEXT,
        Pratyantardasha_Lord TEXT,
        Sookshma_Lord TEXT,
        Prana_Lord TEXT,
        MD_Sign TEXT,
        AD_Sign TEXT,
        PAD_Sign TEXT,
        FOREIGN KEY(Asset_ID) REFERENCES Dim_Asset_Natal(Asset_ID)
    );
    """)
    
    print("Building Dim_Annual_Varshaphala...")
    cursor.execute("""
    CREATE TABLE Dim_Annual_Varshaphala (
        Asset_ID TEXT,
        Trading_Year INTEGER,
        Varsheshwara TEXT,
        Muntha_Sign TEXT,
        Active_Ithasala_Yogas TEXT,
        Active_Easarpha_Yogas TEXT,
        Sun_Pancha_Vargiya_Bala REAL,
        Moon_Pancha_Vargiya_Bala REAL,
        Jupiter_Pancha_Vargiya_Bala REAL,
        PRIMARY KEY (Asset_ID, Trading_Year),
        FOREIGN KEY(Asset_ID) REFERENCES Dim_Asset_Natal(Asset_ID)
    );
    """)
    
    print("Building Fact_ML_Feature_Crosses...")
    cursor.execute("""
    CREATE TABLE Fact_ML_Feature_Crosses (
        Asset_ID TEXT,
        Timestamp TEXT,
        MD_Lord_Natal_Shadbala REAL,
        AD_Lord_Natal_Sub_Lord TEXT,
        Saturn_Transit_vs_Natal_Delta REAL,
        Jupiter_Transit_vs_Natal_Delta REAL,
        Transit_Saturn_over_Natal_Moon_Flag INTEGER,
        Jupiter_Trine_Hit_To_Natal_Venus INTEGER,
        Kota_Chakra_Stambha_Invasion_Count INTEGER,
        USA_Natal_Sade_Sati_Flag INTEGER,
        PRIMARY KEY (Asset_ID, Timestamp),
        FOREIGN KEY(Asset_ID) REFERENCES Dim_Asset_Natal(Asset_ID)
    );
    """)
    
    print("Creating Indexes...")
    cursor.execute("CREATE INDEX idx_transit_date ON Fact_Macro_Transit(Date);")
    cursor.execute("CREATE INDEX idx_dasha_dates ON Fact_Asset_Dasha(Start_Timestamp, End_Timestamp);")
    
    conn.commit()
    conn.close()
    print("Successfully built astrology_universe.db")

if __name__ == "__main__":
    build_database()
