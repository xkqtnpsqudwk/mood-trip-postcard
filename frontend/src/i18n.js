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
        "Tell us how you feel and we'll recommend a corner of the city that matches it. Visit, leave a short review, and we'll turn it into a digital postcard - one trip, many stops, all kept in your archive.",
      startGuestCta: "Continue as guest",
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
      postcardLoginPrompt: "Log in when you're ready to save a visit as a postcard.",
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
      spotsHeading: "Spots that match your feeling",
      continuationHeading: "Where to next on this trip?",
      visitCta: "Write a postcard after visiting →",
      visitCtaGuest: "Write a postcard after visiting →",
      startOver: "Start over with a new mood",
      dismiss: "Just keep the recommendations",
      endTrip: "Finish this trip",
      noMatches:
        "We couldn't find a strong place match yet. Try describing your mood with a little more detail.",
      allVisited:
        "You've visited every spot we recommended for this mood. Time to wrap up the trip!",
      sourceDisclaimer:
        "These are candidate places the AI found from public web sources. Please confirm current hours, access, and safety yourself before visiting.",
    },
    postcardCreator: {
      heading: "After you visit, how was it?",
      subheading:
        "Write what you want the image to remember. If you have photos, we'll use them for the postcard front.",
      placeholder:
        "The light, the street noise, the color of the place, or the feeling you want the image to carry...",
      photoLabel: "Visit photos",
      photoHint:
        "Optional. Add up to 4 photos and AI will turn them into a postcard collage. Leave it empty for an AI-generated image.",
      photoButton: "Choose photos",
      photoLimit: "Only the first 4 photos will be used.",
      photoError: "Couldn't read those photos. Please try different images.",
      back: "Back",
      submit: "Create my postcard",
      loading: "Making your postcard...",
      loadingHint:
        "The AI is creating the postcard image. The back will stay as a blank postcard form.",
    },
    postcard: {
      tapToFlip: "Tap to flip →",
      tapToOpen: "Tap to enlarge →",
      myReview: "My review",
      nextPlaceLabel: "Next place I visited",
      locale: "en-US",
    },
    archive: {
      loading: "Loading your postcards...",
      error: "Couldn't load the archive. Please try again.",
      empty: "No postcards yet — go create your first mood trip!",
      close: "Close",
      stopsCount: (count) => (count === 1 ? "1 stop" : `${count} stops`),
    },
    share: {
      label: "Share card",
      heading: "Save or copy this trip moment",
      download: "Download card",
      copy: "Copy caption",
      native: "Share",
      copied: "Caption copied.",
      copyFailed: "Couldn't copy it. Please try again.",
      downloading: "Creating your share card...",
      downloaded: "Share card downloaded.",
      downloadFailed: "Couldn't create the card. Please try again.",
      shared: "Shared.",
      footer: "Shared from MoodTrip",
      blankPostcardHint: "A blank postcard form with this trip image on the front.",
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
    postcardArrived: "Your postcard has arrived ✉",
    finalPostcard: {
      heading: "Your final trip postcard is ready",
      subheading:
        "We gathered every postcard from this journey into one complete memory.",
      loading: "Making the final postcard...",
    },
    findNextStop: "Find my next stop →",
    endTrip: "Finish this trip",
    planAnother: "Start a whole new trip",
    viewArchive: "View archive",
    errors: {
      analyze:
        "We couldn't read your mood within 90 seconds. Please try again.",
      postcard:
        "We couldn't create your postcard within 90 seconds. Please try again.",
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
        "지금 기분을 알려주시면 그 감정에 어울리는 도시의 한 켠을 추천해드려요. 다녀와서 짧은 후기를 남기면 디지털 엽서로 만들어드립니다 — 하나의 여행에 여러 정거장을 이어가며 보관함에 차곡차곡 기록할 수 있어요.",
      startGuestCta: "게스트로 시작하기",
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
      postcardLoginPrompt: "방문 기록을 엽서로 남길 준비가 되면 로그인해주세요.",
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
      spotsHeading: "지금 기분과 어울리는 장소",
      continuationHeading: "다음 정거장은 어디로 가볼까요?",
      visitCta: "다녀온 뒤 엽서 쓰기 →",
      visitCtaGuest: "다녀온 뒤 엽서 쓰기 →",
      startOver: "새로운 기분으로 다시 시작하기",
      dismiss: "추천만 보고 끝내기",
      endTrip: "여행 마무리하기",
      noMatches:
        "아직 강하게 맞는 장소를 찾지 못했어요. 기분을 조금 더 자세히 적어 다시 시도해보세요.",
      allVisited: "이 기분에 추천된 장소를 모두 다녀오셨어요! 여행을 마무리해보세요.",
      sourceDisclaimer:
        "AI가 공개 웹 정보를 바탕으로 찾은 장소 후보예요. 방문 전 운영 시간, 접근성, 안전 정보는 꼭 직접 확인해주세요.",
    },
    postcardCreator: {
      heading: "다녀온 뒤, 어떠셨나요?",
      subheading: "이미지에 담기길 원하는 장면이나 느낌을 적어주세요. 사진이 있으면 엽서 앞면에 활용할게요.",
      placeholder: "빛, 거리의 소리, 장소의 색감, 이미지에 담고 싶은 분위기를 적어주세요...",
      photoLabel: "방문 사진",
      photoHint: "선택 사항이에요. 최대 4장을 올리면 AI가 콜라주 엽서로 만들고, 없으면 새 이미지를 생성해요.",
      photoButton: "사진 선택하기",
      photoLimit: "처음 4장의 사진만 사용할게요.",
      photoError: "사진을 읽지 못했어요. 다른 이미지로 다시 시도해주세요.",
      back: "뒤로",
      submit: "엽서 만들기",
      loading: "엽서를 만드는 중...",
      loadingHint:
        "AI가 엽서 앞면 이미지를 만드는 중이에요. 뒷면은 빈 엽서 양식으로 남겨둘게요.",
    },
    postcard: {
      tapToFlip: "눌러서 뒤집기 →",
      tapToOpen: "눌러서 크게 보기 →",
      myReview: "나의 후기",
      nextPlaceLabel: "다음 방문한 장소",
      locale: "ko-KR",
    },
    archive: {
      loading: "엽서를 만드는 중...",
      error: "보관함을 불러오지 못했어요. 다시 시도해주세요.",
      empty: "아직 엽서가 없어요 — 첫 감성 여행을 만들어보세요!",
      close: "닫기",
      stopsCount: (count) => `${count}개의 정거장`,
    },
    share: {
      label: "공유 카드",
      heading: "이 여행 순간을 저장하거나 공유하기",
      download: "카드 저장",
      copy: "문구 복사",
      native: "공유하기",
      copied: "공유 문구를 복사했어요.",
      copyFailed: "복사하지 못했어요. 다시 시도해주세요.",
      downloading: "공유 카드를 만드는 중이에요...",
      downloaded: "공유 카드를 저장했어요.",
      downloadFailed: "카드를 만들지 못했어요. 다시 시도해주세요.",
      shared: "공유했어요.",
      footer: "MoodTrip에서 공유",
      blankPostcardHint: "앞면에는 여정 이미지, 뒷면에는 빈 엽서 양식이 있는 카드예요.",
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
    postcardArrived: "엽서가 도착했어요 ✉",
    finalPostcard: {
      heading: "최종 여정 엽서가 완성됐어요",
      subheading: "이번 여정의 모든 엽서를 하나의 완전한 기억으로 모았어요.",
      loading: "엽서를 만드는 중...",
    },
    findNextStop: "다음 정거장 찾기 →",
    endTrip: "여행 마무리하기",
    planAnother: "완전히 새로운 여행 시작하기",
    viewArchive: "보관함 보기",
    errors: {
      analyze: "90초 안에 기분을 분석하지 못했어요. 다시 시도해주세요.",
      postcard: "90초 안에 엽서를 만들지 못했어요. 다시 시도해주세요.",
      finalPostcard: "90초 안에 최종 엽서를 만들지 못했어요. 다시 시도해주세요.",
    },
  },
};

