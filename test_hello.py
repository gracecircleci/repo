html_string = '''
<html>
    <body>
        <h1> CICD Test Runs </h1>

        <!-- *** Section 1 *** --->
        <h2>Section 1: Apple Inc. (AAPL) stock in 2014</h2>
        <p>Apple stock price rose steadily through 2014.</p>
        
        <!-- *** Section 2 *** --->
        <h2>Section 2: AAPL compared to other 2014 stocks</h2>
        <p>GE had the most predictable stock price in 2014.  </p>
    </body>
</html>'''
with open('~/report.html', 'w') as f:
  f.write(html_str)

