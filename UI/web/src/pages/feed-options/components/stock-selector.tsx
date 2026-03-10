import { Autocomplete, FormControl, FormHelperText } from "@mui/joy";
import ShowChart from "@mui/icons-material/ShowChart";
import { STOCKOPTIONS } from "../constants/stock-options.constant";

function StockSelector() {
  return (
    <FormControl sx={{ width: 300, marginBottom: 2 }}>
      <Autocomplete
        multiple
        disableCloseOnSelect
        startDecorator={<ShowChart />}
        placeholder="Select stocks to track"
        options={STOCKOPTIONS}
      />
      <FormHelperText>
        Leave empty to receive news for all stocks
      </FormHelperText>
    </FormControl>
  );
}

export default StockSelector;
