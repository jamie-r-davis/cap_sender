SOURCES = [
    {
        'name': 'cap_applications',
        'pattern': 'ugaappl_{}.zip',
        'dttm_fmt': '%m%d%Y',
        'source': '60abb9fc-d53f-4ec7-82d1-78f8857c4d45',
        'order': 10,
        'destination': '/incoming/oua/commonapp'
    },
    {
        'name': 'cap_forms',
        'pattern': 'ugaapplsform_{}.zip',
        'dttm_fmt': '%m%d%Y',
        'source': '4061d4df-3425-4ce9-a497-e6786d5692d5',
        'order': 20,
        'destination': '/incoming/oua/commonapp'
    },
    {
        'name': 'capx_application_data',
        'pattern': '{}_TR_Applications.txt',
        'dttm_fmt': '%m_%d_%Y',
        'source': '59c95237-6fa0-4761-993e-102a0200b03a',
        'order': 30,
        'destination': '/incoming/oua/commonapp_transfer'
    },
    {
        'name': 'capx_applications',
        'pattern': '{}_TR_Applications.zip',
        'dttm_fmt': '%m_%d_%Y',
        'source': 'ab6535f5-5e77-4a91-b810-f34373f82c5e',
        'order': 40,
        'destination': '/incoming/oua/commonapp_transfer'
    },
    {
        'name': 'capx_college_transcripts',
        'pattern': '{}_TR_College_Transcript.zip',
        'dttm_fmt': '%m_%d_%Y',
        'source': '7577f6b6-03d3-49eb-afa7-f01b3a4e0629',
        'order': 50,
        'destination': '/incoming/oua/commonapp_transfer'
    },
    {
        'name': 'capx_evaluations',
        'pattern': '{}_TR_Evaluations.zip',
        'dttm_fmt': '%m_%d_%Y',
        'source': 'f595fce2-eab6-4e0a-aab3-84a6ee4f9784',
        'order': 60,
        'destination': '/incoming/oua/commonapp_transfer'
    },
]
