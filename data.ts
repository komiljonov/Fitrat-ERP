interface IBonusType {
  value: string;
  price_type: string;
  amount: number;
  name: string;
}

export const Fines: IBonusType[] = [
  //   {
  //     value: "ADMINISTRATOR",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Sinov darsiga yozilib kelmaganlar uchun jarima",
  //   },
  //   {
  //     value: "ADMINISTRATOR",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Sinov darsiga keldi lekin aktivga o‘tmaganligi uchun jarima",
  //   },
  //   {
  //     value: "SERVICE_MANAGER",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Aktivdan ketgan o‘quvchi uchun jarima",
  //   },
  {
    value: "ACCOUNTING",
    price_type: "SUM",
    amount: 0,
    name: "Jami qarzdor o‘quvchilar sonining 69.9% dan kichik bo‘lgan qismi uchu jarima",
  },
  {
    value: "ACCOUNTING",
    price_type: "SUM",
    amount: 0,
    name: "Jami qarzdor o‘quvchilar sonining 70% dan 80% gacha bo‘lgan qismi uchun jarima",
  },
  {
    value: "ACCOUNTING",
    price_type: "SUM",
    amount: 0,
    name: "Jami qarzdor o‘quvchilar sonining 80.1% dan 85% gacha bo‘lgan qismi uchun jarima",
  },
];

export const BonusesItems = [
  //   {
  //     value: "CALL_OPERATOR",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Markazga kelgan o‘quvchi uchun bonus",
  //   },
  //   {
  //     value: "ADMINISTRATOR",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Yaratilgan buyurtma uchun bonus",
  //   },
  //   {
  //     value: "ADMINISTRATOR",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Sinov darsiga kelgan o‘quvchi uchun bonus",
  //   },
  //   {
  //     value: "ADMINISTRATOR",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Aktiv o‘quvchiga aylangan yangi o‘quvchi uchun bonus",
  //   },
  //   {
  //     value: "SERVICE_MANAGER",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Xizmat ko‘rsatgan har bir aktiv o‘quvchi uchun bonus",
  //   },
  {
    value: "ACCOUNTING",
    price_type: "SUM",
    amount: 0,
    name: "Har bir qarzdor bo‘lmagan va aktiv o‘quvchi uchun bonus",
  },
  {
    value: "ACCOUNTING",
    price_type: "SUM",
    amount: 0,
    name: "Jami yangi va aktiv o‘quvchi o‘quvchilarning 93% dan 94.9% gacha bo‘lgan qismi uchun bonus",
  },
  {
    value: "ACCOUNTING",
    price_type: "SUM",
    amount: 0,
    name: "Jami yangi va aktiv o‘quvchi o‘quvchilarning 95% dan 97.9% gacha bo‘lgan qismi uchun bonus",
  },
  {
    value: "ACCOUNTING",
    price_type: "SUM",
    amount: 0,
    name: "Jami yangi va aktiv o‘quvchi o‘quvchilarning 98% dan 99.9% gacha bo‘lgan qismi uchun bonus",
  },
  {
    value: "ACCOUNTING",
    price_type: "SUM",
    amount: 0,
    name: "Jami yangi va aktiv o‘quvchi o‘quvchilarning 100% gacha bo‘lgan qismi uchun bonus",
  },
  //   {
  //     value: "ATTENDANCE_MANAGER",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Aktiv o‘quvchi soniga bonus",
  //   },
  //   {
  //     value: "FILIAL_Manager",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Aktiv o‘quvchi soniga bonus",
  //   },
  //   {
  //     value: "DIRECTOR",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Aktiv o‘quvchi soniga bonus",
  //   },
  //   {
  //     value: "HEAD_TEACHER",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Aktiv o‘quvchi soniga bonus",
  //   },
  //   {
  //     value: "MONITORING_MANAGER",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Aktiv o‘quvchi soniga bonus",
  //   },
  //   {
  //     value: "TESTOLOG",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "Aktiv o‘quvchi soniga bonus",
  //   },
  {
    value: "ASSISTANT",
    price_type: "SUM",
    amount: 0,
    name: "Bir oyda 10 marta kelgan har bir o‘quvchi uchun bonus",
  },
  //   {
  //     value: "TEACHER",
  //     price_type: "SUM",
  //     amount: 0,
  //     name: "O‘quvchi to‘lagan summadan foiz beriladi",
  //   },
];
