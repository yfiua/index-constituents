#!/usr/bin/env python3
# generate footer.html with build timestamp

from datetime import datetime, UTC

# print footer with current timestamp in UTC timezone
print("  <footer>")
print("    <p align='right'><i>Last build:", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S %Z"), "</i></p>")
print("  </footer>")
print("</body>")
print("</html>")
