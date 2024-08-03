# Harbinger

## Description
Harbinger is a web application penetration testing tool. It uses browser HAR file exports to populate a database with HTTP requests made by a target application. It allows a user to edit and re-send requests. It also provides a fuzzing utility for fuzzing interesting requests.

Harbinger is a python GUI application written in tkinter together with ttkbootstrap. Harbinger provides portable Pyinstaller executables for Windows and Linux x86-64, allowing it to be easily executed without installing python or required packages.

## Usage
Before using Harbinger, you must open your browser's developer tools and enable persistent logging. This process may vary depending on the browser, but persistent logging allows you to track network requests between page reloads.

![enable_persistent_logging](https://github.com/user-attachments/assets/f271cbdf-a741-4acd-bd25-8ff38c97ca75)

Once enabled, you keep the developer network tab open while you explore the application, eliciting all the functionality you can through your browser. The network tab will record your requests. When finished, you can simply export the recording as a HAR file.

![export_as_har](https://github.com/user-attachments/assets/aad7e0e1-e043-4938-a4b3-bba3855d12c2)

Once exported, Harbinger can import the HAR file and parse its contents into a Database.

![import](https://github.com/user-attachments/assets/75813ca5-bef1-4e94-8ee9-f1101963a39b)

In one tab you can view a site map.

![site_map](https://github.com/user-attachments/assets/ce10ab60-71cf-481d-aa17-3692f5f3b21e)

In another tab you can see a full history of requests.

![history](https://github.com/user-attachments/assets/e3818b9e-92ac-4f5f-90c6-8727f635c140)

You can right click on a specific request in the site map or history tab and send that request to a request editor.

![send_to_editor](https://github.com/user-attachments/assets/83b3c9f7-0fe0-4227-98b6-774faca77ceb)

The request editor allows you to tamper with a request manually before re-sending it.

![request_editor](https://github.com/user-attachments/assets/3490f6c5-f224-41c7-a283-b7cfb704b121)

A request can also be sent to the fuzzer, where a target can be fuzzed using payload files.

![fuzzer](https://github.com/user-attachments/assets/cee4da3d-994c-47fe-9bb9-2eb18050a536)

## Notes
* Tkinter widgets have limits, and in some cases exhibit unexpected results. This is first seen in the History tab, where to accurately view a request and response, you must doubleclick the row. Single clicks yield an innacurate row in the widget. Meanwhile single clicks work fine in the Site Map. Then when running the fuzzer, reloading Tkinter tables is really glitchy, so a hacky way was contrived to allow the fuzz results to be displayed without a whole refresh, but you can't double click to view the raw request/response until the fuzzing is finished and the table is reloaded. But overall, tkinter and ttkbootstrap can offer some cool widgets with a nice appearance.
* This is a fairly niche tool. It offers portability and simplicity. However, OWASP ZAP and Burp Suite are much more capable, and both have methods to import a HAR file. It was done more as a fun project rather than attempting to really fill a need.
* This tool is for authorized security auditing purposes only.

Happy Hunting!
