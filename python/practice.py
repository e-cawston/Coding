import pandas as pd

# 1. Create the DataFrame - like tibble()
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Euan'],
    'age': [25, 30, 26],
    'score': [88, 92, 95]
})

# 2. Filter: age >= 26
filtered = df['age'] >= 26  # hint: df['age'] >= 26

# 3. Mutate: new column 'grade' 
# Use np.where(condition, value_if_true, value_if_false)
import numpy as np
filtered['grade'] = np.where(filtered['score'] > 90, 'A', 'B')  # hint: np.where(filtered['score'] > 90, 'A', 'B')

# 4. Arrange: sort by score descending
result = filtered.sort_values('score', ascending=False)  # hint: sort_values

print(result)