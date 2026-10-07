// 도로그램(챕터 5 미션 1) 운영 데이터. 학생 화면(feed.html)과 운영자 화면(feed-admin.html)이 같이 읽는다.
// 문구·미션 배정을 바꿀 때는 이 파일만 고치면 된다. 운영실 자료(정답 포함)는 server/ch5_seed.json 에 있다.
window.DOROGRAM = {
  API: '/api/ch5',
  TEAM_COUNT: 10,

  // 확인 기준 4가지 (미션 1에서 배우고 2일차 스캔 검증에서 다시 씀)
  CRITERIA: {
    who:     { label: '작성자',   icon: 'user-round-search', hint: '계정 이름, 가입일, 팔로워 수를 확인합니다. 공식 계정은 @doroland 하나뿐입니다.' },
    when:    { label: '날짜',     icon: 'calendar-clock',    hint: '게시 날짜와 사진 촬영 날짜가 서로 맞는지 확인합니다.' },
    witness: { label: '직접 목격', icon: 'eye',               hint: '"들었는데", "~래요"처럼 건너 들은 말인지, 직접 본 내용인지 확인합니다.' },
    cross:   { label: '자료 대조', icon: 'files',             hint: '사실 카드, 다른 게시물과 내용이 맞는지 대조합니다.' }
  },

  // 게시글 형식 4가지
  FORMATS: {
    news:    { label: '뉴스 기사',   icon: 'newspaper',   authorLabel: '언론사 이름',  titleLabel: '기사 제목', bodyLabel: '기사 본문 (3~5문장)' },
    sns:     { label: 'SNS 게시물',  icon: 'image',       authorLabel: '계정 이름',    titleLabel: null,        bodyLabel: '게시글 내용' },
    story:   { label: '스토리',      icon: 'smartphone',  authorLabel: '계정 이름',    titleLabel: null,        bodyLabel: '사진 위에 올릴 짧은 글' },
    witness: { label: '목격담',      icon: 'message-circle', authorLabel: '글쓴이 이름', titleLabel: '글 제목',      bodyLabel: '내가 본 것 (직접 본 것처럼)' },
    notice:  { label: '공지문',      icon: 'megaphone',   authorLabel: '공지한 곳',    titleLabel: '공지 제목', bodyLabel: '공지 내용' }
  },

  // 가짜를 만들 때 쓰는 수법
  TACTICS: [
    { id: '사칭',          desc: '공식 계정이나 유명 언론사인 척합니다. 계정 이름을 한 글자만 바꾸는 식입니다.' },
    { id: '감정 자극',      desc: '"충격", "긴급", "빨리 퍼뜨려 주세요"처럼 놀라게 해서 확인할 틈을 주지 않습니다.' },
    { id: '가짜 전문가',    desc: '"박사에 따르면"처럼 이름도 소속도 없는 전문가를 내세웁니다.' },
    { id: '사진 바꿔치기',  desc: '다른 날, 다른 곳에서 찍은 사진을 지금 일인 것처럼 씁니다. AI로 사진을 고칠 수도 있습니다.' },
    { id: '날짜 조작',      desc: '옛날 일을 오늘 일처럼, 없었던 날짜를 있었던 것처럼 씁니다.' },
    { id: '편 가르기',      desc: '"코덱스 편 vs 자일로 편"처럼 사람들을 두 편으로 나눠 싸우게 합니다.' }
  ],

  // 조별 미션 카드 (형식 + 수법). 아이들이 올리는 게시물은 모두 "진짜처럼 보이는 가짜"다.
  TEAM_MISSIONS: {
    1:  { format: 'news',    tactic: '사칭' },
    2:  { format: 'sns',     tactic: '사진 바꿔치기' },
    3:  { format: 'witness', tactic: '감정 자극' },
    4:  { format: 'notice',  tactic: '사칭' },
    5:  { format: 'news',    tactic: '가짜 전문가' },
    6:  { format: 'sns',     tactic: '날짜 조작' },
    7:  { format: 'witness', tactic: '편 가르기' },
    8:  { format: 'notice',  tactic: '날짜 조작' },
    9:  { format: 'news',    tactic: '편 가르기' },
    10: { format: 'sns',     tactic: '사진 바꿔치기' }
  },

  // 사실 카드: 판별할 때 "다른 자료와 맞나"의 기준. 가짜를 만들 때도 이걸 보고 그럴듯하게 꾸민다.
  FACTS: [
    '도로랜드 공식 계정은 @doroland (도로랜드 운영실) 하나뿐입니다.',
    '"섬이 사라져 보였다"는 기사는 6년 전, 3년 전, 3일 전에 나왔고 모두 10월 초입니다.',
    '도로랜드 섬이 바다에 잠긴 기록은 한 번도 없습니다.',
    '어제 저녁, 전원이 꺼진 회전목마가 저절로 돌았습니다. 오늘 오전에 점검합니다.',
    '어제 밤 9시 40분쯤 중앙 광장 조명이 한꺼번에 꺼졌다가 10초 뒤 켜졌습니다.',
    '도로랜드 배는 오전 9시부터 오후 6시까지 매시 정각에 출발합니다.',
    '전광판 공지는 운영실에서만 바꿀 수 있습니다.'
  ],

  // 진행 단계 (운영자 화면에서 넘김)
  PHASES: {
    read:   { label: '자료 살펴보기', desc: '도로랜드가 사라졌다는 이야기가 퍼지고 있습니다. 게시물을 읽고 확인 기준 4가지 버튼을 눌러 보세요.' },
    make:   { label: '게시물 만들기', desc: '미션 카드대로 진짜처럼 보이는 가짜 게시물을 만드세요. 올리면 바로 피드에 들어가고, 다른 조에게는 판별 시간부터 보입니다.' },
    judge:  { label: '판별 시간', desc: '피드에 있는 모든 게시물을 진짜인지 가짜인지 판별하세요. 어떤 기준으로 찾았는지 꼭 고르세요.' },
    reveal: { label: '정답 공개', desc: '모든 게시물의 정답과 각 조가 숨긴 단서를 확인하세요.' }
  }
};
