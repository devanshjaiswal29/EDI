import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import mysql.connector

# Step 1: Connect to MySQL Database
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Add password if required
        database="voting"
    )
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as err:
    print("MySQL connection error:", err)
    exit()

# Step 2: Fetch data from MySQL table
print("\nStep 1: Fetching data from MySQL")

query = "SELECT Age, Gender, Caste, Vote FROM votes WHERE Age IS NOT NULL"
cursor.execute(query)
rows = cursor.fetchall()

# Convert to pandas DataFrame
df = pd.DataFrame(rows)

# Step 3: Define demographic groups and parties
ages = ['Up to 25 yrs', '26-35 yrs', '36-45 yrs', '46-55 yrs', '56 yrs and above']
genders = ['Male', 'Female']
castes = ['SC', 'ST', 'OBC', 'General']
parties = ['Congress', 'BJP', 'BSP', 'CPI(M)', 'AAP', 'SP', 'Independent', 'NOTA', 'Others', 'No response']

# Create all possible demographic groups
groups = [(age, gender, caste) for age in ages for gender in genders for caste in castes]

# Filter out 'Missing' age for matrix construction
df = df[df['Age'] != 'Missing']

# Step 4: Create vote proportion matrix
vote_matrix = np.zeros((len(groups), len(parties)))

for i, (age, gender, caste) in enumerate(groups):
    group_data = df[(df['Age'] == age) & (df['Gender'] == gender) & (df['Caste'] == caste)]
    total_voters = len(group_data)
    
    if total_voters > 0:
        vote_counts = group_data['Vote'].value_counts()
        for j, party in enumerate(parties):
            vote_matrix[i, j] = vote_counts.get(party, 0) / total_voters
    else:
        vote_matrix[i, :] = 0

# Step 5: Display and save
vote_matrix_df = pd.DataFrame(
    vote_matrix,
    index=[f"{age}_{gender}_{caste}" for age, gender, caste in groups],
    columns=parties
)

vote_matrix_df.to_csv('vote_proportion_matrix.csv')
print("Vote Proportion Matrix:")
print(vote_matrix_df)

# Heatmap
plt.figure(figsize=(16, 14))
sns.heatmap(vote_matrix_df, annot=True, fmt='.2f', cmap='Blues',
            cbar_kws={'label': 'Vote Proportion'}, annot_kws={'size': 8})
plt.title('Vote Proportion Matrix by Demographic Group')
plt.xlabel('Party')
plt.ylabel('Demographic Group')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plt.savefig('vote_matrix_heatmap.png')
plt.show()

# Cleanup
cursor.close()
conn.close()