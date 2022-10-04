# Developer Guide
1. Clone the repo
2. Make sure that poetry is installed on your computer (How to install 
   [Poetry](https://python-poetry.org/docs/))
3. run `poetry install`
4. Your environment is now ready to run, develop and test **netport**!


# Run

```bash
# Inside the repository
uvicorn netport.netport:app --host 0.0.0.0 --port 80 --reload
```

Open browser at: http://host_ip/docs