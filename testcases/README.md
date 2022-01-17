# Testcase


## Steps need to follow for writing the testcase

- Make sure testcase file format should be like `test_*.py`
- Write the testcase function which should starts with `test_*()`


## How to run testcase 

If you follow the above steps then you can directly run the command. Most recommended way
```commandline
python -m coverage run -m pytest testcases/ -p 'test_*py'
```


And also run the circle ci in local by this command and make sure coverage is more than 80 %
```commandline
circleci local execute --job build
```

