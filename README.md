Preparation:

```
 echo -n 1 1>1
 echo -n 0 1>0
```

```
 curl http://localhost:1234/1/status
 curl -T1 http://localhost:1234/1/status

 curl -H 'Accept: text/plain' http://localhost/1/sync/
```

