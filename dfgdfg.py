class Lead:
    id: str
    name: str

    stage: str


class Group:
    id: str
    name: str


class FirstLesson:

    lead: Lead
    group: Group
