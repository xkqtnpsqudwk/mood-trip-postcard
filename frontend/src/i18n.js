export const translations = {
  en: {
    appTitle: "MoodTrip",
    appSubtitle: "AI-guided Emotional City Travel",
    tabCreate: "Create",
    tabArchive: "Archive",
    tabPersonalization: "My Page",
    cities: { Paris: "Paris", Seoul: "Seoul" },
    landing: {
      title: "MoodTrip",
      tagline: "An AI city travel curator tuned to your mood and taste",
      description:
        "Tell us how you feel and we'll suggest one place that fits your travel style. Visit if you want, save the moment, and finish the trip whenever you're ready to turn your records into a postcard.",
      loginCta: "Log in / Sign up",
      backToIntro: "← Back",
    },
    auth: {
      loginHeading: "Log in",
      signupHeading: "Create an account",
      usernameLabel: "Username",
      passwordLabel: "Password",
      loginSubmit: "Log in",
      signupSubmit: "Sign up",
      switchToSignup: "Don't have an account? Sign up",
      switchToLogin: "Already have an account? Log in",
      loading: "Please wait...",
      loginError: "Couldn't log in. Check your username and password.",
      signupError: "Couldn't sign up. That username may already be taken.",
      logout: "Log out",
      guestLabel: "Browsing as guest",
      postcardLoginPrompt: "Log in when you're ready to save this place as a travel record.",
    },
    personalization: {
      heading: "About me",
      subheading:
        "Write a few sentences about who you are - your personality, what you like or dislike, how you tend to feel in different situations. We'll read it alongside every mood search you make while logged in.",
      placeholder:
        "I'm introverted and like quiet, unhurried places. Crowds wear me out, but I love discovering something unexpected. I'm drawn to old things, soft light, and calm atmospheres...",
      save: "Save my profile",
      saving: "Saving...",
      saved: "Saved! This will apply to your next mood search.",
      loginRequired: "Log in to save your personal profile.",
    },
    moodForm: {
      heading: "Where does your heart want to wander?",
      subheading:
        "Tell us how you feel, and we'll find a city corner that matches your mood.",
      cityLabel: "City",
      moodLabel: "Your mood right now",
      moodPlaceholder:
        "I feel a little restless, like I need to wander somewhere quiet and golden...",
      submit: "Find my mood trip",
      loading: "Reading your mood...",
      loadingHint:
        "The AI is composing your clue — this can take a few minutes, thanks for your patience.",
      personalizationHint: "Want sharper recommendations? Tell us about yourself →",
    },
    recommendation: {
      clueLabel: "Your metaphorical clue",
      mapTitle: "Approximate mood map",
      spotsHeading: "One place for this moment",
      continuationHeading: "One place for your next mood",
      visitCta: "Open trip chat →",
      visitCtaGuest: "Open trip chat →",
      startOver: "Try again with a new mood",
      dismiss: "Finish without a record",
      endTrip: "Finish this trip",
      noMatches:
        "We couldn't find a strong place match yet. Try describing your mood with a little more detail.",
      allVisited:
        "There is no place to show yet. Try describing your mood again.",
      distanceLabel: (km) => `${km} km from your location`,
      sourceDisclaimer:
        "These are candidate places the AI found from public web sources. Please confirm current hours, access, and safety yourself before visiting.",
    },
    visitChat: {
      eyebrow: "Trip companion",
      heading: (place) => `Chat through your time at ${place}`,
      subheading:
        "Talk casually while deciding, moving, staying, or looking back. When the moment feels complete, save it as a record.",
      initial: () =>
        "I'm here. Tell me anything - questions, random thoughts, even if it feels messy.",
      placeholder: "Say anything...",
      send: "Send",
      loading: "MoodTrip is thinking...",
      error: "We couldn't answer within 90 seconds. Please try again.",
      back: "Back to recommendation",
      visited: "Save this moment as a record →",
    },
    postcardCreator: {
      heading: "After you visit, how was it?",
      subheading:
        "Write what you want this moment to remember. If you have photos, we'll use them for a collage.",
      placeholder:
        "The light, the street noise, the color of the place, or the feeling you want this record to carry...",
      photoLabel: "Visit photos",
      photoHint:
        "Optional. Add up to 4 photos and AI will turn them into a travel collage. Leave it empty for an AI-generated image.",
      photoButton: "Choose photos",
      photoLimit: "Only the first 4 photos will be used.",
      photoError: "Couldn't read those photos. Please try different images.",
      back: "Back",
      submit: "Save this moment",
      loading: "Creating this moment...",
      loadingHint:
        "The AI is creating a travel-record image from your note or photos.",
    },
    postcard: {
      tapToFlip: "Tap to flip →",
      tapToOpen: "Tap to enlarge →",
      myReview: "My review",
      nextPlaceLabel: "Next place I visited",
      finalCardLabel: "Trip Postcard",
      locale: "en-US",
    },
    record: {
      cardLabel: "Travel Record",
      momentTitle: (place) => `A moment at ${place}`,
    },
    archive: {
      loading: "Loading your records...",
      error: "Couldn't load the archive. Please try again.",
      empty: "No records yet — start a mood trip and save your first moment.",
      recordsEmpty: "No records yet — visit a recommended place and save your first moment.",
      postcardsEmpty: "No postcards yet — finish a trip after saving at least one record.",
      close: "Close",
      recordsHeading: "Records",
      recordsSubheading: "Moments saved from each place you chose to visit.",
      postcardsHeading: "Postcards",
      recordsCount: (count) => (count === 1 ? "1 record" : `${count} records`),
      postcardsCount: (count) => (count === 1 ? "1 postcard" : `${count} postcards`),
      stopsCount: (count) => (count === 1 ? "1 record" : `${count} records`),
    },
    share: {
      label: "Share",
      heading: "Save or share this postcard image",
      download: "Save image",
      copy: "Copy caption",
      native: "Share",
      copied: "Caption copied.",
      copyFailed: "Couldn't copy it. Please try again.",
      downloading: "Preparing your image...",
      downloaded: "Image saved.",
      downloadFailed: "Couldn't save the image. Please try again.",
      shared: "Shared.",
      caption: ({ city, place, moodText, clue, review }) =>
        [
          `${city} / ${place}`,
          moodText && `Mood: ${moodText}`,
          clue && `"${clue}"`,
          review && `"${review}"`,
          "Shared from MoodTrip",
        ]
          .filter(Boolean)
          .join("\n\n"),
    },
    recordSaved: "This moment was saved to your records.",
    finalPostcard: {
      heading: "Your final trip postcard is ready",
      subheading:
        "We gathered your saved records from this journey into one complete postcard.",
      loading: "Making the final postcard...",
    },
    findNextStop: "Enter a new mood →",
    endTrip: "Finish this trip",
    planAnother: "Start a whole new trip",
    viewArchive: "View archive",
    errors: {
      analyze:
        "We couldn't read your mood within 90 seconds. Please try again.",
      record:
        "We couldn't create this record within 90 seconds. Please try again.",
      finalPostcard:
        "We couldn't create your final trip postcard within 90 seconds. Please try again.",
    },
  },
  ko: {
    appTitle: "MoodTrip",
    appSubtitle: "AI가 안내하는 감성 도시 여행",
    tabCreate: "만들기",
    tabArchive: "보관함",
    tabPersonalization: "마이페이지",
    cities: { Paris: "파리", Seoul: "서울" },
    landing: {
      title: "MoodTrip",
      tagline: "내 기분과 취향에 맞춘 AI 도시 여행 큐레이터",
      description:
        "지금 기분을 알려주시면 나의 여행 성향에 맞는 장소를 한 곳 추천해드려요. 가고 싶다면 다녀와서 순간을 기록하고, 언제든 여행을 마무리하며 기록들을 엽서로 남길 수 있어요.",
      loginCta: "로그인 / 회원가입",
      backToIntro: "← 뒤로",
    },
    auth: {
      loginHeading: "로그인",
      signupHeading: "회원가입",
      usernameLabel: "아이디",
      passwordLabel: "비밀번호",
      loginSubmit: "로그인",
      signupSubmit: "가입하기",
      switchToSignup: "계정이 없으신가요? 회원가입",
      switchToLogin: "이미 계정이 있으신가요? 로그인",
      loading: "잠시만 기다려주세요...",
      loginError: "로그인하지 못했어요. 아이디와 비밀번호를 확인해주세요.",
      signupError: "가입하지 못했어요. 이미 사용 중인 아이디일 수 있어요.",
      logout: "로그아웃",
      guestLabel: "게스트로 이용 중",
      postcardLoginPrompt: "이 장소에서의 순간을 기록으로 저장하려면 로그인해주세요.",
    },
    personalization: {
      heading: "나의 성향",
      subheading:
        "당신이 어떤 사람인지 자유롭게 적어주세요. 성격, 좋아하는 것과 싫어하는 것, 평소 어떤 상황에서 어떤 기분을 느끼는지 같은 걸 알려주시면, 로그인 상태에서 감정 검색을 할 때마다 함께 참고할게요.",
      placeholder:
        "저는 내향적이고 조용하고 느긋한 곳을 좋아해요. 사람 많은 곳에 있으면 금방 지치지만, 예상 못한 걸 발견하는 건 좋아해요. 오래된 것들이나 은은한 빛, 잔잔한 분위기에 끌리는 편이에요...",
      save: "내 성향 저장하기",
      saving: "저장하는 중...",
      saved: "저장했어요! 다음 감정 검색부터 반영됩니다.",
      loginRequired: "나만의 성향을 저장하려면 로그인해주세요.",
    },
    moodForm: {
      heading: "당신의 마음은 지금 어디로 향하고 있나요?",
      subheading:
        "지금 기분을 알려주시면, 그 감정에 어울리는 도시의 한 켠을 찾아드릴게요.",
      cityLabel: "도시",
      moodLabel: "지금 나의 기분",
      moodPlaceholder:
        "왠지 마음이 조금 어수선해서, 조용하고 따스한 곳을 걷고 싶은 기분이에요...",
      submit: "내 감성 여행 찾기",
      loading: "기분을 읽는 중...",
      loadingHint:
        "AI가 단서를 만들고 있어요 — 몇 분 정도 걸릴 수 있으니 잠시만 기다려주세요.",
      personalizationHint: "더 정확한 추천을 원하시나요? 내 성향 알려주기 →",
    },
    recommendation: {
      clueLabel: "당신을 위한 은유적 단서",
      mapTitle: "대략적인 위치",
      spotsHeading: "지금의 한 걸음을 위한 장소",
      continuationHeading: "새로운 기분에 맞춘 다음 장소",
      visitCta: "여정 대화 열기 →",
      visitCtaGuest: "여정 대화 열기 →",
      startOver: "새로운 기분으로 다시 추천받기",
      dismiss: "기록 없이 여행 마무리하기",
      endTrip: "여행 마무리하기",
      noMatches:
        "아직 강하게 맞는 장소를 찾지 못했어요. 기분을 조금 더 자세히 적어 다시 시도해보세요.",
      allVisited: "아직 보여드릴 장소가 없어요. 새로운 기분으로 다시 시도해보세요.",
      distanceLabel: (km) => `현재 위치 기준 ${km}km`,
      sourceDisclaimer:
        "AI가 공개 웹 정보를 바탕으로 찾은 장소 후보예요. 방문 전 운영 시간, 접근성, 안전 정보는 꼭 직접 확인해주세요.",
    },
    visitChat: {
      eyebrow: "여정 동행 대화",
      heading: (place) => `${place}에서의 시간을 함께 이야기해요`,
      subheading:
        "갈지 고민하는 순간부터 머무는 동안, 다녀온 뒤 돌아보는 순간까지 친구처럼 편하게 대화할 수 있어요. 충분히 정리되면 기록으로 남겨요.",
      initial: () =>
        "나한테 뭐든 말해도 돼. 궁금한 거든, 그냥 드는 생각이든, 좀 애매한 기분이든.",
      placeholder: "아무거나 말해줘...",
      send: "보내기",
      loading: "MoodTrip이 답을 준비하고 있어요...",
      error: "90초 안에 답변하지 못했어요. 다시 시도해주세요.",
      back: "추천으로 돌아가기",
      visited: "이 순간 기록으로 남기기 →",
    },
    postcardCreator: {
      heading: "다녀온 뒤, 어떠셨나요?",
      subheading: "이 순간에 남기고 싶은 장면이나 느낌을 적어주세요. 사진이 있으면 콜라주로 활용할게요.",
      placeholder: "빛, 거리의 소리, 장소의 색감, 이 기록에 담고 싶은 분위기를 적어주세요...",
      photoLabel: "방문 사진",
      photoHint: "선택 사항이에요. 최대 4장을 올리면 AI가 여행 콜라주로 만들고, 없으면 새 이미지를 생성해요.",
      photoButton: "사진 선택하기",
      photoLimit: "처음 4장의 사진만 사용할게요.",
      photoError: "사진을 읽지 못했어요. 다른 이미지로 다시 시도해주세요.",
      back: "뒤로",
      submit: "이 순간 저장하기",
      loading: "순간을 기록하는 중...",
      loadingHint:
        "AI가 후기나 사진을 바탕으로 여행 기록 이미지를 만드는 중이에요.",
    },
    postcard: {
      tapToFlip: "눌러서 뒤집기 →",
      tapToOpen: "눌러서 크게 보기 →",
      myReview: "나의 후기",
      nextPlaceLabel: "다음 방문한 장소",
      finalCardLabel: "여행 엽서",
      locale: "ko-KR",
    },
    record: {
      cardLabel: "Travel Record",
      momentTitle: (place) => `${place}에서의 순간`,
    },
    archive: {
      loading: "기록을 불러오는 중...",
      error: "보관함을 불러오지 못했어요. 다시 시도해주세요.",
      empty: "아직 기록이 없어요 — 첫 감성 여행에서 순간을 남겨보세요!",
      recordsEmpty: "아직 기록이 없어요 — 추천 장소를 다녀온 뒤 첫 순간을 저장해보세요.",
      postcardsEmpty: "아직 엽서가 없어요 — 기록을 하나 이상 남긴 뒤 여행을 마무리해보세요.",
      close: "닫기",
      recordsHeading: "기록",
      recordsSubheading: "방문하기로 선택한 장소마다 남긴 순간들이에요.",
      postcardsHeading: "엽서",
      recordsCount: (count) => `${count}개의 기록`,
      postcardsCount: (count) => `${count}개의 엽서`,
      stopsCount: (count) => `${count}개의 기록`,
    },
    share: {
      label: "공유",
      heading: "이 엽서 이미지를 저장하거나 공유하기",
      download: "이미지 저장",
      copy: "문구 복사",
      native: "공유하기",
      copied: "공유 문구를 복사했어요.",
      copyFailed: "복사하지 못했어요. 다시 시도해주세요.",
      downloading: "이미지를 준비하는 중이에요...",
      downloaded: "이미지를 저장했어요.",
      downloadFailed: "이미지를 저장하지 못했어요. 다시 시도해주세요.",
      shared: "공유했어요.",
      caption: ({ city, place, moodText, clue, review }) =>
        [
          `${city} / ${place}`,
          moodText && `오늘의 기분: ${moodText}`,
          clue && `"${clue}"`,
          review && `"${review}"`,
          "MoodTrip에서 공유",
        ]
          .filter(Boolean)
          .join("\n\n"),
    },
    recordSaved: "이 순간이 기록에 저장됐어요.",
    finalPostcard: {
      heading: "최종 여정 엽서가 완성됐어요",
      subheading: "이번 여정의 기록들을 하나의 완전한 엽서로 모았어요.",
      loading: "엽서를 만드는 중...",
    },
    findNextStop: "새로운 기분 입력하기 →",
    endTrip: "여행 마무리하기",
    planAnother: "완전히 새로운 여행 시작하기",
    viewArchive: "보관함 보기",
    errors: {
      analyze: "90초 안에 기분을 분석하지 못했어요. 다시 시도해주세요.",
      record: "90초 안에 기록을 만들지 못했어요. 다시 시도해주세요.",
      finalPostcard: "90초 안에 최종 엽서를 만들지 못했어요. 다시 시도해주세요.",
    },
  },
};
