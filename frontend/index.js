const calcTime = (timestamp) => {
  // 한국 시간 UTC + 9시 기준, 빼주려면 9시간 * 60분 * 60초 * 1000 밀리세컨드
  const curTime = new Date().getTime() - 9 * 60 * 60 * 1000;
  const timeDiff = new Date(curTime - timestamp);
  const hour = timeDiff.getHours();
  const minute = timeDiff.getMinutes();
  const second = timeDiff.getSeconds();

  if (hour > 0) return `${hour}시간 전`;
  else if (minute > 0) return `${minute}분 전`;
  else if (second > 0) return `${second}초 전`;
  else return "방금 전";
};

const renderData = (data) => {
  const main = document.querySelector("main");
  data.reverse().forEach(async (obj) => {
    const Div = document.createElement("div");
    Div.className = "item-list";

    const imgDiv = document.createElement("div");
    imgDiv.className = "item-list__img";

    const img = document.createElement("img");
    const res = await fetch(`/images/${obj.id}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    img.src = url;

    const InfoDiv = document.createElement("div");
    InfoDiv.className = "item-list__info";

    const InfoTitleDiv = document.createElement("div");
    InfoTitleDiv.class = "item-list__info-title";
    InfoTitleDiv.innerText = obj.title;

    const InfoMetaDiv = document.createElement("div");
    InfoMetaDiv.className = "item-list__info-meta";
    InfoMetaDiv.innerText = obj.place + " " + calcTime(obj.createdAt);

    const InfoPriceDiv = document.createElement("div");
    InfoPriceDiv.className = "item-list__info-price";
    InfoPriceDiv.innerText = obj.price;

    imgDiv.appendChild(img);

    InfoDiv.appendChild(InfoTitleDiv);
    InfoDiv.appendChild(InfoMetaDiv);
    InfoDiv.appendChild(InfoPriceDiv);

    Div.appendChild(imgDiv);
    Div.appendChild(InfoDiv);

    main.appendChild(Div);
  });
};

const fetchList = async () => {
  // post 에서 /items 라는 패스에 api를 지정했지만 이번에는 get 요청이기 때문에 둘다 쓸 수 있다
  const res = await fetch("/items");
  const data = await res.json();
  renderData(data);
};

fetchList();
