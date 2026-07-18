import pandas as pd
import os
import sys

# We need to insert saving logic right after extraction in 03_extract_health_data.py
with open("code/03_extract_health_data.py", "r") as f:
    content = f.read()

# For NFHS-6
content = content.replace("    if not nfhs6_df.empty:", "    if not nfhs6_df.empty:\n        nfhs6_df.to_csv(os.path.join(PROC_DIR, 'nfhs6_raw.csv'), index=False)")

# For NFHS-5
content = content.replace("    if not nfhs5_df.empty:", "    if not nfhs5_df.empty:\n        nfhs5_df.to_csv(os.path.join(PROC_DIR, 'nfhs5_raw.csv'), index=False)")

# For RHS
content = content.replace("    if not rhs_df.empty:", "    if not rhs_df.empty:\n        rhs_df.to_csv(os.path.join(PROC_DIR, 'rhs_raw.csv'), index=False)")

with open("code/03_extract_health_data.py", "w") as f:
    f.write(content)
