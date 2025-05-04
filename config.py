"""
Configuration settings for the University Scout application.
"""

# Define file paths and patterns
INSTITUTION_DATA_URL = "data/Most-Recent-Cohorts-Institution.csv"
HISTORICAL_DATA_PATTERN = "data/MERGED*.csv"  # Pattern for historical cohort files
FOS_DATA_PATTERN = "data/FieldOfStudyData*.csv"  # Pattern for Field of Study files
RANKING_FILES = {
    "cwur": "data/cwurData.csv",
    "shanghai": "data/shanghaiData.csv",
    "times": "data/timesData.csv"
}

# Define columns to load initially for main institution data
# Optimized for performance - only essential columns
COLUMNS_TO_LOAD = [
    'UNITID', 'INSTNM', 'CITY', 'STABBR', 'CONTROL', 'INSTURL', 'NPCURL',
    'ADM_RATE', 'SAT_AVG', 'ACTCMMID',
    'TUITIONFEE_IN', 'TUITIONFEE_OUT',
    'UGDS',
    'C150_4',
    'MD_EARN_WNE_P10'
]

# Columns that should be numeric - optimized to match COLUMNS_TO_LOAD
NUMERIC_COLUMNS = [
    'CONTROL', 'ADM_RATE', 'SAT_AVG', 'ACTCMMID', 'UGDS',
    'TUITIONFEE_IN', 'TUITIONFEE_OUT',
    'C150_4', 'MD_EARN_WNE_P10'
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

# Diversity column mapping
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


