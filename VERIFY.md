# VERIFY — public-clone transcript

Public origin verification (HTTPS, unauthenticated):

```sh
rm -rf /tmp/fresh-hn-tls13-hrr
git clone https://github.com/necat101/hn-tls13-hrr-keyshare-boundary-lab.git /tmp/fresh-hn-tls13-hrr
cd /tmp/fresh-hn-tls13-hrr
python3 evaluator.py
cat results.json
cat RESULTS.md
python3 -m unittest tests.test_boundary -v
./verify.sh
git remote -v
git rev-parse HEAD
```

Expected: 9 cases evaluated, 10 tests OK, no live TLS.

