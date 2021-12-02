// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python
// Sergio. Julio 2021

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public class AgentController : MonoBehaviour
{
    List<List<Vector3>> positions;
    public GameObject carPrefab;
    public GameObject trafficLightPrefab;

    int totalCars = 0;
    int totalTrafficLights = 4;

    List<GameObject> cars;
    String[] trafficLights;
    public float timeToUpdate = 4f;
    private float timer;
    float dt;

    // IEnumerator - yield return
    IEnumerator SendData(string data)
    {
        WWWForm form = new WWWForm();
        form.AddField("bundle", "the data");
        string url = "http://localhost:8080";
        using (UnityWebRequest www = UnityWebRequest.Post(url, form))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
            www.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();          // Talk to Python
            if (www.isNetworkError || www.isHttpError)
            {
                Debug.Log(www.error);
            }
            else
            {
                List<Vector3> newPositions = new List<Vector3>();
                string txt = www.downloadHandler.text.Replace('\'', '\"');

                string[] divide = txt.Split(new string[] { "],\"lights\":[" }, StringSplitOptions.None);

                string txtCars = divide[0];
                txtCars = txtCars.TrimStart('{', '\"', 'c', 'a', 'r', 's', '\"', ':', '[');
                txtCars = "{\"" + txtCars;
                
                string[] strs = txtCars.Split(new string[] { "}, {" }, StringSplitOptions.None);
                for (int i = 0; i < strs.Length; i++) {
                    strs[i] = strs[i].Trim();
                    if (i == 0) strs[i] = strs[i] + '}';
                    else if (i == strs.Length - 1) strs[i] = '{' + strs[i];
                    else strs[i] = '{' + strs[i] + '}';
                    Vector3 pos = JsonUtility.FromJson<Vector3>(strs[i]);
                    newPositions.Add(pos);
                }
                positions.Add(newPositions);
                if(positions.Count >= 3){
                    positions.RemoveAt(0);
                }

                string txtLights = divide[1];
                txtLights = txtLights.TrimEnd(']', '}');
                trafficLights = txtLights.Split(new string[] { "," }, StringSplitOptions.None);
            }
        }

    }

    // Start is called before the first frame update
    void Start()
    {
        cars = new List<GameObject>();
        positions = new List<List<Vector3>>();
    }

    // Update is called once per frame
    void Update()
    {
        timer -= Time.deltaTime;
        dt = 1.0f - (timer / timeToUpdate);

        if(timer < 0)
        {
#if UNITY_EDITOR
            timer = timeToUpdate; // reset the timer
            Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);
            string json = EditorJsonUtility.ToJson(fakePos);
            StartCoroutine(SendData(json));
#endif
        }


        if (positions.Count >= 1)
        {
            int actualCars = positions[positions.Count - 1].Count;
            if(positions.Count > 1){
                List<Vector3> last = positions[positions.Count - 1];
                List<Vector3> prevLast = positions[positions.Count - 2];
                int moveCars = prevLast.Count;
                for (int s = 0; s < moveCars; s++)
                {
                    // Interpolate using dt
                    Vector3 interpolated = Vector3.Lerp(prevLast[s], last[s], dt);
                    cars[s].transform.localPosition = interpolated;

                    Vector3 dir = last[s] - prevLast[s];
                    cars[s].transform.rotation = Quaternion.LookRotation(dir);
                }
            }

            if (actualCars > totalCars){
                for(int i = totalCars; i < actualCars; i++){
                    cars.Add(Instantiate(carPrefab, positions[positions.Count - 1][i], Quaternion.identity));
                }
            }
            totalCars = actualCars;
        }
    }
}