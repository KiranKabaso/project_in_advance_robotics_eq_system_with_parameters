======================================================
Finding Grobner Cover for a Parametric Equation System
======================================================

Getting Started
------------------------------------------------------
1. Make sure SageMath and Python are installed.
2. Configure your system swap space (see `setup.txt`).
3. Run:
   • `sage find_grobner_cover.py &`
   • Edit `limits_stats.py` to insert the PID
   • `python limits_stats.py`

Repository Contents
------------------------------------------------------
• `find_grobner_cover.py` – main computation script
• `limits_stats.py` – memory monitor to prevent system crashes
• `setup.txt` – full environment setup instructions
• `test_and_results.txt` – documentation of test outcomes and limitations

Dependencies  
------------------------------------------------------  
• SageMath  
• Python  
• psutil (Python library, install with `pip install psutil`)  
• Linux or WSL2 with large swap enabled


General Explanation
------------------------------------------------------
After the Grobner basis attempt failed, I researched and found a paper  
describing the exact problem I had. In it, the authors explained that  
you can partition the parameter space into regions, each with its own  
Grobner basis. The paper referenced the Montes Grobner Cover algorithm,  
which I discovered is implemented in Singular’s `grobcov.lib`.

General Implementation
-----------------------------------------------------
• Generate the equations.  
• Generate the Singular code.  
• Launch a Singular subprocess that runs until completion.  
• Save the results to a JSON file mapping each Grobner basis to its parametric condition.

Memory Management
------------------------------------------------------
`limits_stats.py` was later added to prevent Singular from using too much  
memory before swapping. When memory usage is critically low, it stops and  
briefly resumes the process to allow the system time to swap.

Results
------------------------------------------------------
• **2 parameters:** Returned a result successfully(immediately).  
• **3 parameters:** Ran for 36 hours and consumed 180 GB of memory before  
  an unexpected reset — root cause undetermined. Detailed in  
  `test_and_results.txt`. Results for more than 3 parameters are  
  presumed and not tested due to memory and time constraints.  
• **>3 parameters:** Untested; expected to require even more memory and time.

Further Testing
------------------------------------------------------
Additional experiments can be conducted using  
`find_grobner_cover.py` and `limits_stats.py` as explained in `setup.txt`.

Eight-Parameter Case
------------------------------------------------------
I firmly believe this program can solve the 8-parameter case given  
enough time and memory, since no better algorithm exists. However,  
the 3-parameter case already takes at least 36 hours and 180 GB,  
so the 8-parameter case will likely require significantly more.

Future Tests  
------------------------------------------------------  
A planned retest of the **3-parameter case** is scheduled for up to one  
week, using a maximum memory limit of **280 GB**. Successfully completing  
this run will help confirm the feasibility and reliability of the  
program.
In addition, running a new test on a **4-parameter case** will help  
estimate the expected runtime and memory requirements for the  
**8-parameter case**.

Author
------------------------------------------------------
Developed by [Kiran Kabaso].  
For questions, contact: kirankabaso@gmail.com
