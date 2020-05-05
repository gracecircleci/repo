import os

xml_str = ''' 
<?xml version="1.0" encoding="UTF-8"?>
<test_result>
    <test_runs>
        <test_run started="STARTED_TS" status="Skipped" duration="14" name="bandTestA" class="BandTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="0" name="bandTestB" class="BandTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="1" name="bandTestC" class="BandTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="1" name="bandTestD" class="BandTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="0" name="bandTestE" class="BandTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="1" name="always_true_A" class="CalcsTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="1" name="always_true_B" class="CalcsTest" package="com.mycomp.devops.demoapp" module="webapp"/>
        <test_run started="STARTED_TS" status="Passed" duration="1" name="always_true_C" class="CalcsTest" package="com.mycomp.devops.demoapp" module="webapp"/>
    </test_runs>
</test_result>
'''

print('Current getcwd:', os.getcwd())
if not os.path.exists('./test-results'):
  os.makedirs('./test-results')
with open('./test-results/report.xml', 'w+') as f:

  f.write(xml_str)

