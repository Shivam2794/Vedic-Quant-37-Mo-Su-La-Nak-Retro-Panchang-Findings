import os
import subprocess

urls = {
    "video_00.mp4": "https://stream.video.skool.com/oGWBkfLV01Qmn73FCNCB02OzvSRb1k01U02GLj36OP7pwDs.m3u8?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ2IiwiZXhwIjoxNzgzNjkzMTI4LCJraWQiOiJPVjIwMHZ6SWZuZFVCNHdXdTAxbDRjb0hrYTVQQUd3TlYwMEtZSkJrQkppVlFrIiwicGxheWJhY2tfcmVzdHJpY3Rpb25faWQiOiIzMDJ2dXNuVG1lbW1QSzllOUpMaWxaUmpnVkJ3T2hTNlVLdGkyWnhJS2V1WSIsInN1YiI6Im9HV0JrZkxWMDFRbW43M0ZDTkNCMDJPenZTUmIxazAxVTAyR0xqMzZPUDdwd0RzIn0.YydRUx6japqp12IzhyuS8m2YxiImskVCmQ_26_6b6hyUZuNqwUBpAeORDKkxaG19Kfppk-O7kY3uzl08P0ipMTEkyacUaK9l0c_yKoYruLWTcNWSWHpNoZgyEQbvT1EoZ5x7S57Nd54nX575oyHt_EPYQaintxX13zqWfETFNxTG07rPgfXmbGYbDLpoHpij9yuH6ymz5I20RNw8dh55zr8JMhiCN9Q9nhUOBoCbsEPPUPAGkxCH1AwjLFvJm1A_dP9HRTfz3HXPTV89JQ8Fcn_IQF0_EICu6If-l2FGzhU1fdRfnw7BaG6eGW07Nhdjn6Z6Te_xUw-WqHWIK7CJcg",
    "video_12.mp4": "https://stream.video.skool.com/WfNVpDLLgm5rbiUdFZ006DkK9exd007EAKjb2F6Ig00nr00.m3u8?token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ2IiwiZXhwIjoxNzgzNjkzMDgzLCJraWQiOiJPVjIwMHZ6SWZuZFVCNHdXdTAxbDRjb0hrYTVQQUd3TlYwMEtZSkJrQkppVlFrIiwicGxheWJhY2tfcmVzdHJpY3Rpb25faWQiOiIzMDJ2dXNuVG1lbW1QSzllOUpMaWxaUmpnVkJ3T2hTNlVLdGkyWnhJS2V1WSIsInN1YiI6IldmTlZwRExMZ201cmJpVWRGWjAwNkRrSzlleGQwMDdFQUtqYjJGNklnMDBucjAwIn0.v2eNXUvFT9OyjOYwDrUfMnBkn2_I3v4VIKkJd1_THWr4f_OHSunkyHcUtOKO_9gsvymNW70MlRrtB8joanCMzx_mOgi3fwSNb6MLSNqAY6vWpk3xZEfs235JR5-CGFzbo4EdT3CcX02NrY7qCnwZRLpDG7du_P2JjWDl3rMOIFzvNeoMF0tfLGvG43uyxBuiiKIVvU_QGJsLDB2ptSArCpf2Gxx75eTWF7hTdnk8IJ_AYWr15srr2OmV4ZsxXW2Gqqc2NVk8WS_rvDa5fotQRZ_XosufbeNjbMqnCXzs-7kIgZ4IQ2r6DzBVb0kQzA5i-tMVpaM5s1WqaH84D8GtQA"
}

out_dir = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\skool_videos_new"
os.makedirs(out_dir, exist_ok=True)

for name, url in urls.items():
    out_path = os.path.join(out_dir, name)
    if os.path.exists(out_path):
        print(f"Skipping {name}, already downloaded.")
        continue
    print(f"Downloading {name}...")
    cmd = [
        "ffmpeg",
        "-y",
        "-i", url,
        "-c", "copy",
        out_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Finished {name}")
