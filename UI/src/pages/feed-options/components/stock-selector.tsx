import { Autocomplete } from "@mui/joy";
import ShowChart from "@mui/icons-material/ShowChart";
import { STOCKOPTIONS } from "../constants/stock-options.constant";

function StockSelector() {
  return (
    <Autocomplete
      multiple
      disableCloseOnSelect
      startDecorator={<ShowChart />}
      placeholder="Select stocks to track"
      options={STOCKOPTIONS}
      sx={{ width: 300, marginBottom: 2 }}
    />
  );
}

export default StockSelector;
