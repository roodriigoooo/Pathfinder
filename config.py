"""
Configuration settings for the University Scout application.
"""

# Define file paths and patterns
INSTITUTION_DATA_URL = "data/Most-Recent-Cohorts-Institution.parquet"
HISTORICAL_DATA_PATTERN = "data/MERGED*.parquet"  # Pattern for historical cohort files
FOS_DATA_PATTERN = "data/FieldOfStudyData*.parquet"  # Pattern for Field of Study files

# Define columns to load initially for main institution data
COLUMNS_TO_LOAD = [
    'UNITID', 'INSTNM', 'CITY', 'STABBR', 'CONTROL', 'INSTURL', 'NPCURL',
    'ADM_RATE', 'SAT_AVG', 'ACTCMMID', 'ADMCON7',  # Added ADMCON7 for test score consideration
    'TUITIONFEE_IN', 'TUITIONFEE_OUT',
    'UGDS',
    'C150_4',
    'MD_EARN_WNE_P10',
    # Student debt information
    'DEBT_MDN',  # Median debt of all students
    'GRAD_DEBT_MDN',  # Median debt for students who completed
    'WDRAW_DEBT_MDN',  # Median debt for students who withdrew
    'FEMALE_DEBT_MDN',  # Median debt for female students
    'MALE_DEBT_MDN',  # Median debt for male students
    'FIRSTGEN_DEBT_MDN',  # Median debt for first-generation students
    'NOTFIRSTGEN_DEBT_MDN',  # Median debt for non-first-generation students
    'GRAD_DEBT_MDN_SUPP',  # Supplementary completion debt data
    'FTFTPCTFLOAN',  # Percent of first-time, full-time undergraduates with federal loans
    # Student diversity by race
    'UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
    'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN',
    # Student diversity by gender
    'UGDS_MEN', 'UGDS_WOMEN',
    # Staff diversity by race
    'IRPS_WHITE', 'IRPS_BLACK', 'IRPS_HISP', 'IRPS_ASIAN',
    'IRPS_AIAN', 'IRPS_NHPI', 'IRPS_2MOR', 'IRPS_NRA', 'IRPS_UNKN',
    # Staff diversity by gender
    'IRPS_MEN', 'IRPS_WOMEN',
    # Net price data
    'NPT4_PUB', 'NPT4_PRIV',  # Average net price for all students
    # Net price by income brackets
    'NPT41_PUB', 'NPT42_PUB', 'NPT43_PUB', 'NPT44_PUB', 'NPT45_PUB',  # Public institutions
    'NPT41_PRIV', 'NPT42_PRIV', 'NPT43_PRIV', 'NPT44_PRIV', 'NPT45_PRIV'  # Private institutions
]

# Columns that should be numeric - optimized to match COLUMNS_TO_LOAD
NUMERIC_COLUMNS = [
    'CONTROL', 'ADM_RATE', 'SAT_AVG', 'ACTCMMID', 'UGDS',
    'TUITIONFEE_IN', 'TUITIONFEE_OUT',
    'C150_4', 'MD_EARN_WNE_P10',
    # Debt columns
    'DEBT_MDN', 'GRAD_DEBT_MDN', 'WDRAW_DEBT_MDN',
    'FEMALE_DEBT_MDN', 'MALE_DEBT_MDN',
    'FIRSTGEN_DEBT_MDN', 'NOTFIRSTGEN_DEBT_MDN',
    'GRAD_DEBT_MDN_SUPP', 'FTFTPCTFLOAN',
    # Student diversity by race
    'UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN',
    'UGDS_AIAN', 'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN',
    # Student diversity by gender
    'UGDS_MEN', 'UGDS_WOMEN',
    # Staff diversity by race
    'IRPS_WHITE', 'IRPS_BLACK', 'IRPS_HISP', 'IRPS_ASIAN',
    'IRPS_AIAN', 'IRPS_NHPI', 'IRPS_2MOR', 'IRPS_NRA', 'IRPS_UNKN',
    # Staff diversity by gender
    'IRPS_MEN', 'IRPS_WOMEN',
    # Net price data
    'NPT4_PUB', 'NPT4_PRIV',
    'NPT41_PUB', 'NPT42_PUB', 'NPT43_PUB', 'NPT44_PUB', 'NPT45_PUB',
    'NPT41_PRIV', 'NPT42_PRIV', 'NPT43_PRIV', 'NPT44_PRIV', 'NPT45_PRIV'
]

# State abbreviation to full name mapping
STATE_NAMES = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'DC': 'District of Columbia',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'AS': 'American Samoa',
    'GU': 'Guam',
    'MP': 'Northern Mariana Islands',
    'PR': 'Puerto Rico',
    'FM': 'Federated States of Micronesia',
    'PW': 'Palau',
    'VI': 'Virgin Islands',
    'MH': 'Marshall Islands'
}

# Student diversity column mapping
DIVERSITY_MAPPING = {
    'UGDS_WHITE': 'White',
    'UGDS_BLACK': 'Black',
    'UGDS_HISP': 'Hispanic',
    'UGDS_ASIAN': 'Asian',
    'UGDS_AIAN': 'American Indian/Alaska Native',
    'UGDS_NHPI': 'Native Hawaiian/Pacific Islander',
    'UGDS_2MOR': 'Two or More Races',
    'UGDS_NRA': 'Non-Resident Alien',
    'UGDS_UNKN': 'Unknown'
}

# Staff diversity column mapping
STAFF_DIVERSITY_MAPPING = {
    'IRPS_WHITE': 'White',
    'IRPS_BLACK': 'Black',
    'IRPS_HISP': 'Hispanic',
    'IRPS_ASIAN': 'Asian',
    'IRPS_AIAN': 'American Indian/Alaska Native',
    'IRPS_NHPI': 'Native Hawaiian/Pacific Islander',
    'IRPS_2MOR': 'Two or More Races',
    'IRPS_NRA': 'Non-Resident Alien',
    'IRPS_UNKN': 'Unknown'
}

# Gender mapping
GENDER_MAPPING = {
    'UGDS_MEN': 'Male Students',
    'UGDS_WOMEN': 'Female Students',
    'IRPS_MEN': 'Male Staff',
    'IRPS_WOMEN': 'Female Staff'
}


