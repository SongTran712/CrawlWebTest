indexMapping = {
    "properties":{
        "Price":{
            "type":"text"
        },
        "Area":{
            "type":"text"
        },
        "Position":{
            "type":"text"
        },
        "Type":{
            "type":"text"
        },
        "Benefit":{
            "type":"text"
        },
        "SummaryVector":{
            "type":"dense_vector",
            "dims": 768,
            "index":True,
            "similarity": "l2_norm"
        }

    }
}