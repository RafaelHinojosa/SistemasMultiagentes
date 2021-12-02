using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TrafficLightChangeColor : MonoBehaviour
{
    private Material materialSemaforo;
    private readonly int _emissiveColor = Shader.PropertyToID("_emissiveColor");
    private readonly int _baseColor = Shader.PropertyToID("_baseColor");
    
    private Color colorEmissive = new Color();
    private Color baseColor = new Color();
    
    void Start()
    {
        materialSemaforo = gameObject.GetComponent<MeshRenderer>().material;
    }

    void changeColor(bool state) {
        if (state == true) {
            prendeVerde();
        }
        else {
            prendeRojo();
        }
    }

    void prendeRojo() {
        colorEmissive = Color.red;
        baseColor = Color.red;
        interfazSemaforo();
    }

    void prendeVerde() {
        colorEmissive = Color.green;
        baseColor = Color.green;
        interfazSemaforo();
    }

    void interfazSemaforo() {
        materialSemaforo.SetColor(_emissiveColor, colorEmissive);
        materialSemaforo.SetColor(_baseColor, baseColor);
    }
}
