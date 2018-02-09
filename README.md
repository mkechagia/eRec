# eRec

Exception handling recommendations for the right usage of APIs in client apps.

* Data:

The used approach is data-driven and has been applied on three data sets:

1. ten versions of the Android API (14-23). See [1] and [2].

2. 3,539 Android apps from [3].

3. almost 1 million stack traces from [4].

References:

[1] https://github.com/Sable/android-platforms (Android references up to version 17).

[2] https://developer.android.com/reference/classes.html (Folder android-platforms-new in the repo contains Android references from version 18 to version 23.)

[3] N. Viennot, E. Garcia, J. Nieh, A measurement study of Google Play, in: The 2014 ACM International Conference on Measurement and Modeling of Computer Systems, SIGMETRICS ’14, ACM, New York, NY, USA, 2014, pp. 221–233. doi:10.1145/2591971.2592003. (Note: https://archive.org/details/android_apps).

[4] Maria Kechagia, Dimitris Mitropoulos, and Diomidis Spinellis. 2015. Charting the API minefield using software telemetry data. Empirical Softw. Engg. 20, 6 (December 2015), 1785-1830. DOI=http://dx.doi.org/10.1007/s10664-014-9343-7.

* Dependencies:

For the analysis of the Android API and apps, we have used the Soot framework [3] and its Dexpler module [4].

[3] https://sable.github.io/soot/

[4] https://www.abartel.net/dexpler/

* License:

'''
Copyright 2018 Maria Kechagia
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
