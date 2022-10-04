// ==UserScript==
// @name         Academic Writing Assistant
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Help non-native English researchers to write
// @author       AlbertShen
// @match        *://*.overleaf.com/*
// @require      https://unpkg.com/jquery@3.6.0/dist/jquery.min.js
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==

(function() {

    $(
        '<div style="border: 2px dashed rgb(149, 252, 251); width: 330px; height: 330px; position: fixed; bottom: 0; right: 0; z-index: 99999; background-color: rgba(184, 247, 255, 0.9); overflow-x: auto; padding: 1em;">' +
          '<div>' +
            '<div id="AWAModelState"> Can not connect to AI assistant </div>' +
              '<select id="AWAModelType" name="AWAModelType">' +
                '<option value="origin"> origin model </option>' +
                '<option value="quantized"> quantized model </option>' +
              '</select>' +
              '<button id="AWALoadModel">load model</button>' +
            '</div>' +
            '<div>' +
              '<h2 id="AWATitle">Prompt</h2>' +
              '<div id="AWAPrompt" style="margin-top: 1em;">' +
            '</div>' +
          '</div>' +
        '</div>'
    ).appendTo("body");

    GM_xmlhttpRequest({
        method: "GET",
        url: "http://localhost:8000/api/check_model_state",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        },

        onload: function(response){
            let result = JSON.parse(response.responseText);
            if(result.state == "success") {
                if(result.type == "not loaded"){
                    $("#AWAModelState").text("Model not loaded");
                } else if(result.type == "quantized"){
                    $("#AWAModelState").text("Quantized model loaded");
                } else {
                    $("#AWAModelState").text("Origin model loaded");
                }
            } else {
                $("#AWAModelState").text("Error occured when checking model state");
            }
        },
        onerror: function(response){
            console.log(response.responseText);
            $("#AWAModelState").text("Error occured when loading model");
        }
    });

    $("#AWALoadModel").click(function(event){
        $("#AWAModelState").text("Loading model, please wait");
        let model_data = "quantized=";
        if($("#AWAModelType").val() == "origin"){
            model_data += "false";
        } else {
            model_data += "true";
        }
        GM_xmlhttpRequest({
            method: "POST",
            url: "http://localhost:8000/api/init_model",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
            },
            data: model_data,

            onload: function(response){
                let result = JSON.parse(response.responseText);
                if(result.state == "success") {
                    if(result.type == "quantized"){
                        $("#AWAModelState").text("Quantized model loaded");
                    } else {
                        $("#AWAModelState").text("Origin model loaded");
                    }
                } else {
                    $("#AWAModelState").text("Error occured when loading model");
                }
            },
            onerror: function(response){
                console.log(response.responseText);
                $("#AWAModelState").text("Error occured when loading model");
            }
        });
    });

    document.addEventListener('copy',function(e){
        let clipboardData = e.clipboardData || window.clipboardData;
        if(!clipboardData) return ;
        let clipPromise = navigator.clipboard.readText();
        clipPromise.then(function(clipText){
            $("#AWAPrompt").empty();
            $("#AWAPrompt").append("<div> Processing ... </div>");
            GM_xmlhttpRequest({
                method: "POST",
                url: "http://localhost:8000/api/generate",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
                },
                data: "masked_input_str=" + clipText,

                onload: function(response){
                    let result = JSON.parse(response.responseText);
                    if(result.state == "success") {
                        console.log(result.msg);
                        $("#AWAPrompt").empty();
                        for(var item of result.msg){
                            $("#AWAPrompt").append("<div>" + item + "</div>")
                        }
                    } else {
                        $("#AWAPrompt").empty();
                        $("#AWAPrompt").append("<div>" + result.msg + "</div>")
                    }
                },
                onerror: function(response){
                    console.log(response.responseText);
                }
            });
        })
    });
    })();